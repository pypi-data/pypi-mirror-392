import json

from .abstracts import (
    Container,
    Field,
    FieldMapper,
    FieldTypes,
    InsertUpdateUpsertTable,
    PaginatedTable,
    RestAPIPlatform,
)


class BaserowPlatform(RestAPIPlatform):
    PLATFORM = "baserow"

    LIST_LEVELS = [0, 1]

    def __init__(
        self, platform_root_path=None, secret_string=None, alias=None, options=None
    ):
        if not (secret_string):
            raise RuntimeError("Airtable Platform requires secret_string")
        super().__init__(
            platform_root_path=platform_root_path
            if platform_root_path
            else "https://api.baserow.io",
            secret_string=secret_string,
        )

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
        if level == 0:
            # List databases (applications)
            response = self.get("api/applications/")
            return [
                {
                    "id": app["id"],
                    "name": app["name"],
                }
                for app in response
                if app["type"]
                == "database"  # Ensure we only return database applications
            ]
        elif level == 1:
            # List tables within a database
            if parent is None:
                raise ValueError("Parent (database_id) is required for listing tables")

            response = self.get(f"api/database/tables/database/{parent}/")
            return [
                {
                    "id": table["id"],
                    "name": table["name"],
                }
                for table in response
            ]
        else:
            raise ValueError(f"Unsupported level: {level}")

    def create_object(self, object_name, level, parent=None):
        super().create_object(object_name, level, parent=parent)
        raise NotImplementedError("not yet implemented")


class BaserowTable(PaginatedTable, InsertUpdateUpsertTable):
    PLATFORM_CLASS = BaserowPlatform

    UPSERT = False

    BULK_SIZE_INSERT = 200  # Default number of records for bulk queries
    BULK_SIZE_UPDATE = 200  # Default number of records for bulk queries
    BULK_SIZE_GET = 200
    offset_mode = PaginatedTable.OFFSET_MODE_VALUE_PAGE

    NATIVE_ID_NAME = "id"

    def __init__(
        self,
        alias,
        platform: RestAPIPlatform,
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
        # Baserow base
        self.base_id = api_identifier.split("/")[0]

        # Baserow table
        self.table_id = api_identifier.split("/")[1]

        self.insert_endpoint = f"api/database/rows/table/{self.table_id}/batch"
        self.update_endpoint = f"api/database/rows/table/{self.table_id}/batch"
        self.get_endpoint = f"api/database/rows/table/{self.table_id}"
        # self.schema_endpoint = f"meta/bases/{self.base_id}/tables"

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be used to check
        if the credential is valid to query the table.
        """
        try:
            endpoint = f"api/database/fields/table/{self.table_id}/"
            self.log(f"Querying table schema at endpoint {endpoint}", level="debug")
            table_schema = self.platform.get(endpoint)  # type: ignore

            table_columns = [field["name"] for field in table_schema]
            table_name = self.platform.get(f"database/tables/{self.table_id}/")["name"]  # type: ignore

            return self.make_object_info_response(
                isOk=True, detail="", columns=table_columns, name=table_name
            )

        except Exception as e:
            return self.make_object_info_response(
                isOk=False,
                detail=f"Error fetching table {self.table_id} information: {str(e)}",
                columns=[],
                name="",
            )

    #########################################
    ############ Get table items ############
    #########################################

    def get_table_schema(self):
        """
        returns a list of Tableclone Fields
        """
        raise NotImplementedError("get_table_schema() method not yet implemented")

    def get_bulk_raw_data(self, offset=0, modified_after=None):
        """
        Build query and get raw data for a bulk of items
        """
        super().get_bulk_raw_data(offset, modified_after=modified_after)

        params = {
            "page": offset + 1,  # Baserow uses page numbers starting from 1
            "size": self.BULK_SIZE_GET,
        }

        filters = []
        if modified_after:
            filters.append(
                {
                    "field": "Last modified on",  # Assuming this is the field name for last modified
                    "type": "date_after",
                    "value": modified_after,
                }
            )

        if filters:
            params["filters"] = json.dumps({"filter_type": "AND", "filters": filters})  # type: ignore

        r = self.platform.get(self.get_endpoint, params=params)  # type: ignore

        return r

    def bulk_raw_data_to_records(self, response):
        """
        Converts raw data returned by the platform to dict (records style).

        Airtable response format:
        {
            "records": [
                {
                "createdTime": "2022-09-12T21:03:48.000Z",
                "fields": {
                    "Address": "333 Post St",
                    "Name": "Union Square",
                    "Visited": true
                },
                "id": "rec560UJdUtocSouk"
                },
                {
                "createdTime": "2022-09-12T21:03:48.000Z",
                "fields": {
                    "Address": "1 Ferry Building",
                    "Name": "Ferry Building"
                },
                "id": "rec3lbPRG4aVqkeOQ"
                }
            ]
        }
        """
        super().bulk_raw_data_to_records(response)
        records = [
            merge_two_dicts({self.table_index_name(): record["id"]}, record["fields"])
            for record in response["records"]
        ]
        return records

    def is_last_bulk(self, response, offset):
        """
        Determines if this is the last bulk to fetch.
        """
        return response["next"] is None

    #############################################
    ############ Insert/Update items ############
    #############################################

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row"""
        return {"fields": row.to_dict()}

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        return {"id": index, "fields": row.to_dict()}

    def make_record_upsert_from_df_row(self, row):
        """Make a record for update queries frome a DataFrame row"""
        return {"fields": row.to_dict()}

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """
        return {"records": bulk, "typecast": self.typecast}

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        return {"records": bulk, "typecast": self.typecast}

    def make_bulk_upsert_body(self, bulk, unique_id_column):
        """
        Make upsert query body from list of records
        """
        return {
            "records": bulk,
            "typecast": self.typecast,
            "performUpsert": {"fieldsToMergeOn": [unique_id_column]},
        }

    def insert_query(self, body):
        """
        Http call to insert a bulk of items
        """
        super().insert_query(body)
        self.platform.post(self.insert_endpoint, json=body)  # type: ignore

    def update_query(self, body):
        """
        Http call to update a bulk of items
        """
        super().update_query(body)

        self.platform.patch(self.update_endpoint, json=body)  # type: ignore

    def upsert_query(self, body):
        """
        Http call to upsert a bulk of items
        """
        super().upsert_query(body)
        self.platform.patch(self.update_endpoint, json=body)  # type: ignore

    ## Note : dealing with options
    ## Note : date normalization only for compare ?

    def dump_df(self, df):
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
        raise NotImplementedError("list_children() method not yet implemented")
