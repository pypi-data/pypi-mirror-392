import json
from base64 import b64encode

import pandas as pd

from .abstracts import Platform, Table


class KsaarPlatform(Platform):
    PLATFORM = "ksaar"
    BULK_SIZE_INSERT = 10  # Default number of records for bulk queries
    BULK_SIZE_UPDATE = 10  # Default number of records for bulk queries
    BULK_SIZE_GET = 100
    API_SLEEP_TIME = 1
    LIST_LEVELS = [0, 1]

    def __init__(
        self, platform_root_path=None, secret_string=None, alias=None, options=None
    ):
        if platform_root_path:
            self.log(
                f"Provided platform_root_path ({platform_root_path}) will be overriden with https://api.ksaar.co/v1"
            )
        if not (secret_string):
            raise RuntimeError("Ksaar Platform requires secret_string")
        super().__init__(
            platform_root_path="https://api.ksaar.co/v1", secret_string=secret_string
        )
        # Ksaar paging is page offset.
        self.offset_mode = Table.OFFSET_MODE_VALUE_PAGE

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
        encoded_token = b64encode(self.token.encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {encoded_token}"}

    def _list_children_impl(self, level, parent=None):
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """
        if level == 0:
            # Fetching app list
            endpoint = "applications"
            base_list = self.get(endpoint)["results"]
            return self._make_list_response(base_list)

        elif level == 1:
            # Fetching table list
            endpoint = "applications/" + parent + "/workflows"
            tables = self.get(endpoint)["results"]
            return self._make_list_response(tables)

    def create_object(self, object_name, level, parent=None):
        super().create_object(object_name, level, parent=parent)
        raise NotImplementedError("not yet implemented")


class KsaarTable(Table):
    PLATFORM_CLASS = KsaarPlatform

    UPSERT = False

    def __init__(
        self,
        alias,
        platform: Platform,
        api_identifier,
        options={},
        **kwargs,
    ):
        super().__init__(alias, platform, api_identifier, options=options)
        # Ksaar require "pages" offser mode
        self.offset_mode = Table.OFFSET_MODE_VALUE_PAGE

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)

        # Ksaar app
        self.base_id = api_identifier.split("/")[0]

        # Ksaar workflow
        self.table_id = api_identifier.split("/")[1]

        self.insert_endpoint = "records/bulkCreate"
        self.update_endpoint = "records/bulkUpdate"
        self.get_endpoint = "workflows/" + self.table_id + "/records"

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        endpoint = "workflows/" + self.table_id + "/fields"
        self.log("Querying field list endpoint %s" % (endpoint), "debug")
        fields = self.platform.get(endpoint)
        table_columns = [field["name"] for field in fields]
        ksaar_meta_columns = [
            "id",
            "createdAt",
            "updatedAt",
            "userId",
            "workflowId",
        ]
        return self.make_object_info_response(
            isOk=True, detail="", columns=(table_columns + ksaar_meta_columns), name=""
        )

    #########################################
    ############ Get table items ############
    #########################################

    def get_bulk_raw_data(self, offset=0, modified_after=None):
        """
        Build query and get raw data for a bulk of items
        """
        super().get_bulk_raw_data(offset, modified_after=None)

        r = self.platform.get(
            self.get_endpoint,
            # Ksaar pages starts at 1 while iterator from abstract.Table starts at 0
            params={"page": offset + 1, "limit": self.platform.BULK_SIZE_GET},
        )
        return r

    def bulk_raw_data_to_records(self, response):
        """
        Converts raw data returned by the platform to dict (records style).
        Dict must contain a key named as DATAFRAME_INDEX_NAME
        """
        super().bulk_raw_data_to_records(response)
        records = response["results"]
        # We rename _id key to platform.DATAFRAME_INDEX_NAME
        tableclone_records = []
        for record in records:
            record[self.platform.DATAFRAME_INDEX_NAME] = record.pop("id")
            tableclone_records.append(record)

        return tableclone_records

    def is_last_bulk(self, response, offset=None):
        """
        Determines if is last bulk to fetch.
        """
        if response["lastPage"] <= offset:
            return True
        else:
            return False

    def get_all_as_df(self, json_normalize=True, modified_after=None):
        # overriding json_normalize to true
        if modified_after:
            self.log(
                "modified_after have been provided but is not implemented for ksaar"
            )
        return super().get_all_as_df(json_normalize=json_normalize, modified_after=None)

    def sanitize_df(self, df, date_normalize=False):
        # Specific Ksaar normalizing
        # flattening single select
        # json_normalize will flatten single select to .value / .optionId
        for column in df.columns:
            if (
                column.endswith(".value")
                and column.replace(".value", ".optionId") in df.columns
            ):
                # Removing ".value" from name
                df[column[0:-6]] = df[column]
        df = super().sanitize_df(df, date_normalize=date_normalize)
        return df

    #############################################
    ############ Insert/Update items ############
    #############################################

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row"""
        return {"email": self.email, "form": row.to_dict()}

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        return {"id": index, "form": row.to_dict()}

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """
        return {"workflowId": self.table_id, "records": bulk}

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        return {"applicationId": self.base_id, "records": bulk}

    def insert_query(self, body):
        """
        Http call to insert a bulk of items
        """
        super().insert_query(body)
        self.platform.post(self.insert_endpoint, json=body)

    def update_query(self, body):
        """
        Http call to update a bulk of items
        """
        super().update_query(body)
        self.platform.post(self.update_endpoint, json=body)

    def upsert_query(self, body):
        """
        Http call to upsert a bulk of items
        """
        raise NotImplementedError("upsert_query not implemented")

    def map_field_name_to_uuid(self, df):
        """
        Insert and update queries in Ksaar requires uuid to reference
        fields instead of field name
        """
        self.log("Mapping column name to Ksaar UUID")
        # Fetching fields UUID
        fields = self.platform.get(f"workflows/{self.table_id}/fields")

        # Transform into Pandas column mapping to rename columns
        fld_name_uuid_mapping = {}
        for field in fields:
            if field["name"] in df.columns:
                fld_name_uuid_mapping.update({field["name"]: field["id"]})

        # Applying mapping
        df = df.rename(columns=fld_name_uuid_mapping)
        return df

    def insert(self, df):
        df = self.map_field_name_to_uuid(df)
        # KSAAR needs a valid email to create records
        # TEMP : getting first user email
        self.email = self.platform.get(f"applications/{self.base_id}/users")["results"][
            0
        ]["email"]
        self.log(f"Using first user email for new records: {self.email}")
        super().insert(df)

    def update(self, df):
        df = self.map_field_name_to_uuid(df)
        super().update(df)

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
