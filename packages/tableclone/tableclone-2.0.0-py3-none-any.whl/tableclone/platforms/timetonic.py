import json

from ..utils import merge_two_dicts
from .abstracts import Platform, Table


class TimetonicPlatform(Platform):
    PLATFORM = "timetonic"

    BULK_SIZE_INSERT = 10  # Default number of records for bulk queries
    BULK_SIZE_UPDATE = 10  # Default number of records for bulk queries
    BULK_SIZE_GET = 100
    LIST_LEVELS = [0, 1]

    def __init__(
        self, platform_root_path=None, secret_string=None, alias=None, options=None
    ):
        if platform_root_path:
            self.log(
                f"Provided platform_root_path ({platform_root_path}) will be overriden with https://timetonic.com/live/api.php"
            )
        if not (secret_string):
            raise RuntimeError("Timetonic Platform requires secret_string")
        super().__init__(
            platform_root_path="https://timetonic.com/live/api.php",
            secret_string=secret_string,
        )

    def parse_auth_information(self, secret_string):
        """
        Process secret string or other auth information. Checks that enough information is provided
        and that there are no conflicting information
        """
        super().parse_auth_information(secret_string)

        (userid, sesskey) = secret_string.rsplit(":", 1)

        self.userid = userid
        self.sesskey = sesskey

    def headers(self):
        """
        Returns headers with auth
        """
        super().headers()
        # Auth token is passed in query/x-form params
        return {}

    def auth_params(self):
        """
        Auth is handled with query or x-form params in timetonic
        """
        return {"o_u": self.userid, "u_c": self.userid, "sesskey": self.sesskey}

    def get(self, endpoint=None, **kwargs):
        """
        Returns parsed response JSON
        """
        params_ = self.auth_params()
        if kwargs.get("params"):
            params_.update(kwargs.get("params"))

        kwargs["params"] = params_
        return super().get(endpoint, **kwargs)

    def post(self, endpoint=None, **kwargs):
        """ """
        data_ = self.auth_params()
        if kwargs.get("data"):
            data_.update(kwargs.get("data"))

        kwargs["data"] = data_
        return super().post(endpoint, **kwargs)

    def _list_children_impl(self, level, parent=None):
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """

        if level == 0:
            # API doc requires POST but seems that GET also work
            books = self.get(params={"req": "getAllBooks"})["allBooks"]["books"]
            # We filter books with API rights
            base_list = [
                {"id": book["b_o"] + "/" + book["b_c"], "name": book["b_c"]}
                for book in books
                if (self.userid, "1")
                in [(member["u_c"], member["apiRight"]) for member in book["members"]]
            ]
            # self.logger.info("API return : %s " % (base_list))
            return self._make_list_response(base_list)

        elif level == 1:
            # Fetching table list
            (book_owner, book_code) = parent.split("/")
            tables = self.get(
                params={"req": "getBookTables", "b_o": book_owner, "b_c": book_code}
            )["bookTables"]["categories"]
            # self.logger.info("API return : %s " % (tables))
            return self._make_list_response(
                [{"id": table["id"], "name": table["name"]} for table in tables]
            )

    def create_object(self, object_name, level, parent=None):
        super().create_object(object_name, level, parent=parent)
        raise NotImplementedError("not yet implemented")


class TimetonicTable(Table):
    PLATFORM_CLASS = TimetonicPlatform

    UPSERT = False

    TIMETONIC_IGNORED_META = [
        "Comments",
        "Updates",
    ]  # We ignore this as it is complex structured data

    def __init__(
        self,
        alias,
        platform: Platform,
        api_identifier,
        options={},
        **kwargs,
    ):
        super().__init__(alias, platform, api_identifier, options=options)
        self.tmp_row_id = 0  # TimeTonic asks for temp id to insert new row. As it is a dict we must keep unicity

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)

        # Timetonic book is defined by book owner and book code and view?
        self.book_owner = api_identifier.split("/")[0]
        self.book_code = api_identifier.split("/")[1]
        self.table = api_identifier.split("/")[2]

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """

        fields = self.platform.get(
            params={
                "req": "getTableValues",
                "b_o": self.book_owner,
                "b_c": self.book_code,
                "catId": self.table,
            }
        )["tableValues"]["fields"]
        table_columns = [
            field["name"]
            for field in fields
            if field["name"] not in self.TIMETONIC_IGNORED_META
        ]
        return self.make_object_info_response(
            isOk=True, detail="", columns=table_columns, name=""
        )

    #########################################
    ############ Get table items ############
    #########################################

    def get_bulk_raw_data(self, offset=0, modified_after=None):
        """
        Build query and get raw data for a bulk of items
        """
        super().get_bulk_raw_data(offset, modified_after=None)
        return self.platform.get(
            params={
                "req": "getTableValues",
                "b_o": self.book_owner,
                "b_c": self.book_code,
                "catId": self.table,
                "format": "rows",
                "offset": offset,
                "maxRows": self.platform.BULK_SIZE_GET,
            }
        )

    def bulk_raw_data_to_records(self, response):
        """
        Converts raw data returned by the platform to dict (records style).
        Dict must contain a key named as DATAFRAME_INDEX_NAMEÒ
        """
        super().bulk_raw_data_to_records(response)

        # we merge unique id to the record
        records = [
            merge_two_dicts(
                {Platform.DATAFRAME_INDEX_NAME: row["id"]},
                {
                    key: row["fields"][key]["value"]
                    for key in row["fields"].keys()
                    if key not in self.TIMETONIC_IGNORED_META
                },
            )
            for row in response["tableValues"]["rows"]
        ]
        return records

    def is_last_bulk(self, response, offset=None):
        """
        Determines if is last bulk to fetch.
        """
        # ineficient cause need to get next bulk, but couldnt find other solution
        next_bulk = self.get_bulk_raw_data(offset + self.platform.BULK_SIZE_GET)
        if len(next_bulk["tableValues"]["rows"]) == 0:
            return True
        else:
            return False

    #############################################
    ############ Insert/Update items ############
    #############################################

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row"""
        self.tmp_row_id = self.tmp_row_id + 1
        return {"tmp_" + str(self.tmp_row_id): row.to_dict()}

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        return {index: row.to_dict()}

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """
        body = {}
        for record in bulk:
            body.update(record)
        return body

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        body = {}
        for record in bulk:
            body.update(record)
        return body

    def insert_query(self, body):
        """
        Http call to insert a bulk of items
        """
        super().insert_query(body)
        # TimeTonic API require json "body" as query string parameter or x-form param
        data_ = {"req": "createOrUpdateTableRows", "rows": json.dumps(body)}

        self.platform.post(data=data_)

    def update_query(self, body):
        """
        Http call to update a bulk of items
        """
        super().update_query(body)

        # TimeTonic API require json "body" as query string parameter or x-form param
        data_ = {"req": "createOrUpdateTableRows", "rows": json.dumps(body)}

        self.platform.post(data=data_)

    def upsert_query(self, body):
        """
        Http call to upsert a bulk of items
        """
        raise NotImplementedError("upsert_query not implemented")

    def map_field_name_to_uuid(self, df):
        # Fetching fields UUID
        fields = self.platform.get(
            params={
                "req": "getTableValues",
                "b_o": self.book_owner,
                "b_c": self.book_code,
                "catId": self.table,
                "offset": 0,
                "maxRows": self.platform.BULK_SIZE_GET,
            }
        )["tableValues"]["fields"]

        # Transform into Pandas column mapping to rename columns
        fld_name_uuid_mapping = {}
        for field in fields:
            if field["name"] in df.columns:
                # Field ID must be converted to string as TimeTonic requires str field ID for inserts/updates
                fld_name_uuid_mapping.update({field["name"]: str(field["id"])})

        # Applying mapping
        self.log(
            f"Mapping column names to column IDs : {fld_name_uuid_mapping}",
            level="debug",
        )
        df = df.rename(columns=fld_name_uuid_mapping)
        return df

    def update(self, df):
        df = self.map_field_name_to_uuid(df)
        super().update(df)

    def insert(self, df):
        df = self.map_field_name_to_uuid(df)
        super().insert(df)

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
