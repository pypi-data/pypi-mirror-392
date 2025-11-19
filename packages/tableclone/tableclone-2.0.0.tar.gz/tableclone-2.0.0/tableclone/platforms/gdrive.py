import json
from base64 import b64encode

import gspread
import pandas as pd
from oauth2client.client import AccessTokenCredentials

from .abstracts import Container, Platform, Table


class GdrivePlatform(Platform):
    PLATFORM = "gdrive"
    # BULK_SIZE_INSERT = 100  # Default number of records for bulk queries
    # BULK_SIZE_UPDATE = 100  # Default number of records for bulk queries
    # BULK_SIZE_GET = 100
    # API_SLEEP_TIME = 1

    def __init__(
        self, platform_root_path=None, secret_string=None, alias=None, options=None
    ):
        if platform_root_path:
            self.log(
                f"Provides platform_root_path ({platform_root_path}) will be overriden with https://www.googleapis.com"
            )
        if not (secret_string):
            raise RuntimeError("Gdrive Platform requires secret_string")
        super().__init__(
            platform_root_path="https://www.googleapis.com", secret_string=secret_string
        )
        credentials = AccessTokenCredentials(self.token, None)
        self.gspread_client = gspread.authorize(credentials)

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

        TODO: make recursive ? can be any level folders etc ?
        TODO: add type in list_response
        """
        raise NotImplementedError("list() method not yet implemented")

    def create_object(self, object_name, level, parent=None):
        """
        Create a new object (Table, Database...) depending on level.

        level 0: folder
        level 1: workbook
        level 2: worksheet
        """
        super().create_object(object_name, level, parent=parent)
        if level == 1:
            sh = self.gspread_client.create(
                object_name, folder_id=parent
            )  # works id api_identifier is a folder
            self.log(f"New spreadsheet workbook created ({sh.id})")
            return sh.id
        else:
            raise NotImplementedError("create_object not yet implemented")


class GsheetTable(Table):
    PLATFORM_CLASS = GdrivePlatform

    UPSERT = False

    def __init__(
        self,
        alias,
        platform: GdrivePlatform,
        api_identifier,
        options=None,
        **kwargs,
    ):
        """
        GsheetTable is either a spreadsheed with a single worksheet (id 0), or a specific
        worksheet in a spreadsheet

        Args:
            api_identifier(str): {spreadsheet ID}/{workbook GID}
        """
        super().__init__(alias, platform, api_identifier, options=options)
        self.platform = platform  # just for IDE helpstring

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)

        # Spreadsheet (workbook) id
        self.spreadsheet_id = api_identifier.split("/")[0]

        # Worksheet id
        try:
            self.worksheet_id = api_identifier.split("/")[1]
        except IndexError as e:
            self.log(
                f"api_identifier does not seem to contain a sheet id. Using sheet 0 as default",
                level="warning",
            )
            self.worksheet_id = 0

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        sh = self.platform.gspread_client.open_by_key(
            self.spreadsheet_id
        )  # works if api_identifier is a file
        ws = sh.get_worksheet_by_id(self.worksheet_id)
        headers = ws.row_values(1)
        return self.make_object_info_response(
            isOk=True, detail=None, columns=headers, name=ws.title
        )

    #########################################
    ############ Get table items ############
    #########################################

    def get_bulk_raw_data(self, offset=0):
        """
        Build query and get raw data for a bulk of items
        """
        super().get_bulk_raw_data(offset)

        raise NotImplementedError("method not yet implemented")

    def bulk_raw_data_to_records(self, response):
        """
        Converts raw data returned by the platform to dict (records style).
        Dict must contain a key named as DATAFRAME_INDEX_NAME
        """
        super().bulk_raw_data_to_records(response)
        raise NotImplementedError("method not yet implemented")

    def is_last_bulk(self, response, offset=None):
        """
        Determines if is last bulk to fetch.
        """
        raise NotImplementedError("method not yet implemented")

    #############################################
    ############ Insert/Update items ############
    #############################################

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row"""
        raise NotImplementedError("method not yet implemented")

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        raise NotImplementedError("method not yet implemented")

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """
        raise NotImplementedError("method not yet implemented")

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        raise NotImplementedError("method not yet implemented")

    def insert_query(self, body):
        """
        Http call to insert a bulk of items
        """
        super().insert_query(body)
        raise NotImplementedError("method not yet implemented")

    def update_query(self, body):
        """
        Http call to update a bulk of items
        """
        super().insert_query(body)
        raise NotImplementedError("method not yet implemented")

    def upsert_query(self, body):
        """
        Http call to upsert a bulk of items
        """
        raise NotImplementedError("upsert_query not implemented")

    def dump_df(self, df):
        """
        Dumps a dataframe to an existing Table, preserves ID, deletes all data and repopulate with new data

        Args:
            df (DataFrame): Dataframe of data to dump

        Returns:
            str: New table API Identifier
        """
        super().dump_df(df)

        sh = self.platform.gspread_client.open_by_key(
            self.spreadsheet_id
        )  # works if api_identifier is a file
        ws = sh.get_worksheet_by_id(self.worksheet_id)
        self.log("Clearing worksheet")
        ws.clear()
        self.log("Dumping data")
        result = ws.update(
            [df.columns.values.tolist()] + df.fillna("").applymap(str).values.tolist()
        )
        self.log(result, level="debug")


class GdriveFolderContainer(Container):
    PLATFORM_CLASS = GdrivePlatform

    def __init__(
        self, alias, platform: GdrivePlatform, api_identifier, options=None, **kwargs
    ):
        super().__init__(alias, platform, api_identifier, options=options, **kwargs)
        # TODO: call table info

    def parse_api_identifier(self, api_identifier):
        self.gdrive_folder_id = api_identifier

    def dump_df_to_new_table(self, df, table_name):
        """
        Dumps a dataframe to a new Table having Container for parent

        Args:
            df (DataFrame): Dataframe of data to dump
            table_name: Name to be given to newly created table

        Returns:
            Table: New Table object
        """
        super().dump_df_to_new_table(df, table_name)
        new_spreadsheet_id = self.platform.create_object(
            table_name, 1, self.gdrive_folder_id
        )
        new_table = GsheetTable(table_name, self.platform, new_spreadsheet_id, None)
        new_table.dump_df(
            df,
            table_name=None,
            keep_existing_records=False,
            preserve_existing_columns=False,
        )
        return new_table

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        response = self.platform.get(f"drive/v3/files/{self.api_identifier}")
        if response.get("mimeType") == "application/vnd.google-apps.folder":
            return self.make_object_info_response(True, None, [], response["name"])
        else:
            return self.make_object_info_response(
                False,
                f"Is {self.api_identifier} a google drive folder ID ?",
                None,
            )
