import json
import time

import pandas as pd
import requests

from .abstracts import (
    Container,
    Field,
    InsertUpdateUpsertTable,
    PaginatedTable,
    RestAPIPlatform,
)


class BubblePlatform(RestAPIPlatform):
    PLATFORM = "bubble"

    def __init__(self, platform_root_path=None, secret_string=None, alias=None, options=None):
        if not (platform_root_path):
            raise RuntimeError("Bubble Platform requires platform_root_path")
        if not (secret_string):
            raise RuntimeError("Bubble Platform requires secret_string")
        super().__init__(platform_root_path=platform_root_path, secret_string=secret_string)
        self.swagger_url = self.platform_root_path.replace("/obj", "/meta/swagger.json")

    def parse_auth_information(self, secret_string):
        """
        Process secret string or other auth information. Checks that enough information is provided
        and that there are no conflicting information
        """
        super().parse_auth_information(secret_string)
        self.token = secret_string

    def headers(self):
        """
        Returns headers with auth
        """
        super().headers()
        return {"Authorization": f"Bearer {self.token}"}

    def _list_children_impl(self, level, parent=None):
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """
        if level == 0:
            # Fetching base list

            self.log("Querying swagger %s" % (self.swagger_url))
            swagger_dict = requests.get(self.swagger_url).json()

            app_endpoints = list(swagger_dict["paths"].keys())

            table_list = [
                {
                    "id": endpoint.replace("/obj/", "").replace("/{UniqueID}", ""),
                    "name": endpoint.replace("/obj/", "").replace("/{UniqueID}", ""),
                }
                for endpoint in app_endpoints
                if (endpoint.startswith("/obj") and endpoint.endswith("{UniqueID}"))
                # indentifies table endpoint in swagger
            ]
            self.log("Identified tables : %s" % (table_list))
            return self._make_list_response(table_list)

    def create_object(self, object_name, level, parent=None):
        super().create_object(object_name, level, parent=parent)
        raise NotImplementedError("not yet implemented")


class BubbleTable(PaginatedTable, InsertUpdateUpsertTable):
    PLATFORM_CLASS = BubblePlatform

    BULK_SIZE_INSERT = 100  # Default number of records for bulk queries
    BULK_SIZE_UPDATE = 1  # Default number of records for bulk queries
    BULK_SIZE_GET = 100
    BULK_SIZE_DELETE = 1  # Bubble only supports single record deletes

    UPSERT = False

    NATIVE_ID_NAME = "bubble_id_"

    def __init__(
        self,
        alias,
        platform: BubblePlatform,
        api_identifier,
        options={},
        **kwargs,
    ):
        super().__init__(alias, platform, api_identifier, options=options)

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)

        # Bubble table table
        self.table_id = api_identifier

        self.insert_endpoint = self.table_id + "/bulk"
        self.update_endpoint = self.table_id
        self.get_endpoint = self.table_id

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        columns_swagger = []
        try:
            # First try swagger json
            # https://appname.bubbleapps.io/api/1.1/meta/swagger.json

            swagger_url = self.platform.swagger_url  # type: ignore
            self.log("Calling swagger URL %s" % (swagger_url), level="debug")
            r = requests.get(swagger_url)

            columns_swagger = list(
                r.json()["definitions"][self.api_identifier]["properties"].keys()
            )
            self.log(
                "Identified colmuns %s with swagger page" % (columns_swagger),
                level="debug",
            )
        except Exception as e:
            self.log(e.__class__.__name__ + " - " + str(e))
            pass

        self.log("Querying %s table" % (self.table_id), level="debug")

        r = self.platform.get(self.table_id)  # type: ignore
        df = pd.DataFrame(r["response"]["results"])

        api_columns = df.columns.to_list()

        columns = list(set(api_columns + columns_swagger))

        return self.make_object_info_response(isOk=True, detail="", columns=columns, name="")

    #########################################
    ############ Get table items ############
    #########################################

    def get_bulk_raw_data(self, offset=0, modified_after=None):
        """
        Build query and get raw data for a bulk of items
        """
        super().get_bulk_raw_data(offset, modified_after=modified_after)
        params_ = {"cursor": offset, "limit": self.BULK_SIZE_GET}
        if modified_after:
            params_["constraints"] = json.dumps(  # type: ignore
                [
                    {
                        "key": "Modified Date",
                        "constraint_type": "greater than",
                        "value": modified_after,
                    }
                ]
            )
        r = self.platform.get(  # type: ignore
            self.get_endpoint,
            params=params_,
        )
        return r

    def bulk_raw_data_to_records(self, response):
        """
        Converts raw data returned by the platform to dict (records style).
        Dict must contain a key named as DATAFRAME_INDEX_NAME

        Bubble response format
        {
            "cursor": 0,
            "results": [
                {
                    "foo_field_1": "value1",
                    "foo_field_2": "value2",
                    "_id": "item1_bubble_id"
                },
                {
                    "foo_field_1": "value3",
                    "foo_field_2": "value4",
                    "_id": "item2_bubble_id"
                },
                ...
            ],
            "remaining": 0,
            "count": 31
        }
        """
        super().bulk_raw_data_to_records(response)
        records = response["response"]["results"]
        # We rename _id key to platform.DATAFRAME_INDEX_NAME
        tableclone_records = []
        for record in records:
            record[self.table_index_name()] = record.pop("_id")
            tableclone_records.append(record)

        return tableclone_records

    def is_last_bulk(self, response, offset=None):
        """
        Determines if is last bulk to fetch.
        """
        if response["response"]["remaining"] == 0:
            return True
        else:
            return False

    #############################################
    ############ Insert/Update items ############
    #############################################

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row"""
        return row.to_dict()

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        values = row.to_dict()

        # we rename unique ID to _id
        values["_id"] = index

        return values

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """

        return "\n".join([json.dumps(item) for item in bulk])

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        # Bubble only supports update record 1 by 1
        return bulk[0]

    def insert_query(self, body):
        """
        Http call to insert a bulk of items.

        Bubble's bulk insert API returns multiple JSON objects (one per line),
        not a single JSON object, so we need special handling.
        """
        super().insert_query(body)

        # Make the request but don't parse as JSON yet
        url = self.platform.platform_root_path + "/" + self.insert_endpoint  # type: ignore
        headers_ = self.platform.headers()  # type: ignore
        headers_.update({"Content-Type": "text/plain"})

        r = requests.post(url, headers=headers_, data=body)
        self.platform._handle_http_error(r)  # type: ignore
        time.sleep(self.platform.API_SLEEP_TIME)  # type: ignore

        # Parse multi-line JSON response (one JSON object per line)
        response_text = r.text.strip()
        if not response_text:
            return []

        results = []
        for line in response_text.split("\n"):
            if line.strip():
                results.append(json.loads(line))

        return results

    def update_query(self, body):
        """
        Http call to update a bulk of items.

        Bubble's PATCH API may return empty response, so we need special handling.
        """
        super().update_query(body)

        # Make the request but handle empty response
        record_id = body.pop("_id")
        url = self.platform.platform_root_path + "/" + self.update_endpoint + "/" + record_id  # type: ignore

        r = requests.patch(url, headers=self.platform.headers(), json=body)  # type: ignore
        self.platform._handle_http_error(r)  # type: ignore
        time.sleep(self.platform.API_SLEEP_TIME)  # type: ignore

        # Try to parse JSON, but handle empty response
        response_text = r.text.strip()
        if response_text:
            try:
                return r.json()
            except json.JSONDecodeError:
                return {}
        return {}

    def upsert_query(self, body):
        """
        Http call to upsert a bulk of items
        """
        raise NotImplementedError("upsert_query not implemented")

    def make_bulk_delete_body(self, bulk_ids):
        """
        Make delete query body from list of IDs

        Bubble DELETE API deletes one record at a time:
        DELETE /api/1.1/obj/typename/{UniqueID}

        Args:
            bulk_ids: List of IDs (should contain only 1 ID due to BULK_SIZE_DELETE=1)

        Returns:
            str: Single ID to delete
        """
        # With BULK_SIZE_DELETE=1, bulk_ids will always have exactly 1 element
        return bulk_ids[0]

    def delete_query(self, body):
        """
        Http call to delete a single item.

        Bubble DELETE API:
        DELETE /api/1.1/obj/typename/{UniqueID}

        Args:
            body: Single ID string from make_bulk_delete_body
        """
        self.log("Deleting items")

        # Make the request but handle empty response
        url = self.platform.platform_root_path + "/" + self.table_id + "/" + body  # type: ignore

        r = requests.delete(url, headers=self.platform.headers())  # type: ignore
        self.platform._handle_http_error(r)  # type: ignore
        time.sleep(self.platform.API_SLEEP_TIME)  # type: ignore

        # Try to parse JSON, but handle empty response
        response_text = r.text.strip()
        if response_text:
            try:
                return r.json()
            except json.JSONDecodeError:
                return {}
        return {}

    def dump_df(
        self,
        df,
    ):
        """
        Dumps a dataframe to an existing Table, preserves ID, deletes all data and repopulate with new data

        Args:
            df (DataFrame): Dataframe of data to dump

        Returns:
            str: New table API Identifier
        """
        super().dump_df(
            df,
        )
        raise NotImplementedError("list() method not yet implemented")

    def get_table_schema(self) -> list["Field"]:
        super().get_table_schema()
        raise NotImplementedError("get_table_schema method not yet implemented")


class BubbleBase(Container):
    PLATFORM_CLASS = BubblePlatform
    CHILD = BubbleTable  # Update with child class

    def parse_api_identifier(self, api_identifier):
        super().parse_api_identifier(api_identifier)

    def _object_info_impl(self):
        r = requests.get(self.platform.swagger_url)  # type: ignore
        r.raise_for_status()
        return self.make_object_info_response(isOk=True, detail="", columns=[], name="")

    def dump_df_to_new_table(self, df, table_name):
        raise NotImplementedError("dump_df_to_new_table method not implemented")

    def create_table_from_schema(self, table_name, schema, relations=False):
        raise NotImplementedError("create_table_from_schema method not implemented")
