import pandas as pd

from ..utils import Option, OptionSet, merge_two_dicts
from .abstracts import (
    Container,
    Field,
    FieldMapper,
    FieldTypes,
    InsertUpdateUpsertTable,
    PaginatedTable,
    RestAPIPlatform,
)

OPT_TYPECAST = Option(
    "typecast",
    "If set to true, Airtable will try to convert string values into the appropriate cell value. See https://airtable.com/developers/web/api/update-multiple-records#request-typecast",
    bool,
    False,
)

OPT_EXTRA_GET_PARAMS = Option(
    "extra_get_params",
    "Extra parameters to be added to the GET request. See https://airtable.com/developers/web/api/list-records#request-parameters",
    dict,
    {},
)


class AirtablePlatform(RestAPIPlatform):
    PLATFORM = "airtable"

    LIST_LEVELS = [0, 1]

    FIELD_MAPPING = FieldMapper(
        {
            "multilineText": FieldTypes.STRING,
            "singleLineText": FieldTypes.STRING,
            "multipleSelects": FieldTypes,
            "singleSelect": FieldTypes.STRING,
            "email": FieldTypes.STRING,
            "url": FieldTypes.STRING,
            "multipleRecordLinks": FieldTypes.RELATION,
            "checkbox": FieldTypes.BOOLEAN,
            "formula": FieldTypes.STRING,
            # "formula.number.0": FieldTypes.STRING,
            "count": FieldTypes.INTEGER,
            "rollup": FieldTypes.STRING,
            # rollup.singleLineText ?
            "number": FieldTypes.NUMBER,
            "number.0": FieldTypes.INTEGER,
            "number.1": FieldTypes.NUMBER,
            "dateTime": FieldTypes.DATETIME,
            "date": FieldTypes.DATE,
            "richText": FieldTypes.STRING,
            "multipleAttachments": FieldTypes.ATTACHMENTS,
            "multipleLookupValues": FieldTypes.STRING,
            "button": FieldTypes.STRING,
            "autoNumber": FieldTypes.INTEGER,
            "lastModifiedTime": FieldTypes.DATETIME,
            "createdBy": FieldTypes.STRING,
            "lastModifiedBy": FieldTypes.STRING,
            "createdTime": FieldTypes.DATETIME,
            "percent": FieldTypes.NUMBER,
            "singleCollaborator": FieldTypes.STRING,
            "duration": FieldTypes.NUMBER,
            "externalSyncSource": FieldTypes.STRING,
            "currency": FieldTypes.NUMBER,
            "aiText": FieldTypes.STRING,
            "manualSort": FieldTypes.INTEGER,
            "rating": FieldTypes.INTEGER,
            "multipleCollaborators": FieldTypes.STRING,
            "phoneNumber": FieldTypes.STRING,
        },
        {
            FieldTypes.INTEGER: {"type": "number", "options": {"precision": 8}},
            FieldTypes.NUMBER: {"type": "number", "options": {"precision": 8}},
            FieldTypes.STRING: {"type": "multilineText"},
            FieldTypes.BOOLEAN: {
                "type": "checkbox",
                "options": {"color": "greenBright", "icon": "check"},
            },
            FieldTypes.DATE: {
                "type": "date",
                "options": {
                    "dateFormat": {"name": "local"},
                },
            },
            FieldTypes.DATETIME: {
                "type": "dateTime",
                "options": {
                    "timeZone": "utc",
                    "dateFormat": {"name": "local"},
                    "timeFormat": {"name": "24hour"},
                },
            },
            FieldTypes.RELATION: {"type": "multipleRecordLinks"},
            FieldTypes.ATTACHMENTS: {"type": "multipleAttachments"},
        },
    )

    def __init__(
        self, platform_root_path=None, secret_string=None, alias=None, options=None
    ):
        if not (secret_string):
            raise RuntimeError("Airtable Platform requires secret_string")
        super().__init__(
            platform_root_path="https://api.airtable.com/v0",
            secret_string=secret_string,
        )
        if platform_root_path:
            self.log(
                f"Provided platform_root_path ({platform_root_path}) will be overriden with https://api.airtable.com/v0"
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
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """
        if level == 0:
            # Fetching base list
            endpoint = "meta/bases"
            base_list = self.get(endpoint)["bases"]
            self.log("API return : %s " % (base_list), level="debug")
            return self._make_list_response(base_list)

        elif level == 1:
            if parent:
                # Fetching table list
                endpoint = "meta/bases/" + parent + "/tables"
                base_schema = self.get(endpoint)
                self.log("API return : %s " % (base_schema), level="debug")
                table_list = [
                    {"id": f"{parent}/{table['id']}", "name": table["name"]}
                    for table in base_schema["tables"]
                ]
                return self._make_list_response(table_list)
            else:
                raise RuntimeError("Parent not provided")

    def create_object(self, object_name, level, parent=None):
        super().create_object(object_name, level, parent=parent)
        raise NotImplementedError("not yet implemented")


class AirtableTable(PaginatedTable, InsertUpdateUpsertTable):
    PLATFORM_CLASS = AirtablePlatform
    OPTION_SET = OptionSet(
        InsertUpdateUpsertTable.OPTION_SET.options
        + [OPT_TYPECAST, OPT_EXTRA_GET_PARAMS]
    )
    UPSERT = True
    NATIVE_ID_NAME = "record_id"

    platform: RestAPIPlatform

    def __init__(
        self,
        alias,
        platform: RestAPIPlatform,
        api_identifier,
        options={},
        **kwargs,
    ):
        super().__init__(alias, platform, api_identifier, options=options)
        self.typecast = self.option_values.get(OPT_TYPECAST)

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)
        # Airtable base
        self.base_id = api_identifier.split("/")[0]

        # Airtable table
        self.table_id = api_identifier.split("/")[1]

        self.insert_endpoint = f"{self.base_id}/{self.table_id}"
        self.update_endpoint = f"{self.base_id}/{self.table_id}"
        self.delete_endpoint = f"{self.base_id}/{self.table_id}"
        self.get_endpoint = f"{self.base_id}/{self.table_id}"
        self.schema_endpoint = f"meta/bases/{self.base_id}/tables"

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        try:
            endpoint = "meta/bases/" + self.base_id + "/tables"
            self.log("Querying base schema at endpoint %s" % (endpoint), level="debug")
            base_schema = self.platform.get(endpoint)  # type: ignore
            table_schema = [
                tbl for tbl in base_schema["tables"] if tbl["id"] == self.table_id
            ][0]
            table_columns = [field["name"] for field in table_schema["fields"]]
            return self.make_object_info_response(
                isOk=True, detail="", columns=table_columns, name=""
            )

        except IndexError:
            return self.make_object_info_response(
                isOk=False,
                detail="Table %s does not seem to exists" % (self.table_id),
                columns=[],
                name="",
            )

    #########################################
    ############ Get table items ############
    #########################################

    def sanitize_df(self, df, date_normalize=False) -> pd.DataFrame:
        df = super().sanitize_df(df, date_normalize)

        # Airtable long text have 100 000 chars max
        airtable_max_text_length = 100000
        for col_name in df:
            try:
                if df[col_name].str.len().max() > airtable_max_text_length:
                    df[col_name] = df[col_name].str.slice(0, airtable_max_text_length)
                    self.log(
                        f"Column {col_name} have been truncated to {airtable_max_text_length} caracters",
                        level="warning",
                    )
            except Exception:
                # Column is not a string
                pass

        return df

    def get_table_schema(self):
        """
        returns a list of Tableclone Fields
        """
        super().get_table_schema()
        base_schema = self.platform.get(self.schema_endpoint)  # type: ignore
        table_schema = [
            table for table in base_schema["tables"] if table["id"] == self.table_id
        ][0]

        tableclone_table_schema = []
        for airtable_field in table_schema["fields"]:
            if airtable_field["type"] == "multipleRecordLinks":
                tableclone_table_schema.append(
                    Field(
                        self.platform,
                        airtable_field["name"],
                        airtable_field["type"],
                        airtable_field["options"]["linkedTableId"],
                    )
                )
            else:
                tableclone_table_schema.append(
                    Field(self.platform, airtable_field["name"], airtable_field["type"])
                )

        return tableclone_table_schema

    def set_airtable_next_offset(self, bulk_raw_data):
        """
        Stores the Airtable next iteration ID
        """
        self.offset = bulk_raw_data.get("offset")
        self.log(f"Next Airtable offset : {self.offset}", level="debug")

    def get_bulk_raw_data(self, offset=0, modified_after=None):
        """
        Build query and get raw data for a bulk of items
        """
        super().get_bulk_raw_data(offset, modified_after=modified_after)
        endpoint = self.get_endpoint
        params_ = self.option_values.get(OPT_EXTRA_GET_PARAMS) or {}

        if modified_after:
            params_ = {
                **params_,
                **{"filterByFormula": f'LAST_MODIFIED_TIME()>"{modified_after}"'},
            }
        if offset == 0:
            r = self.platform.get(endpoint, params=params_)  # type: ignore
            # Airtable offset is not a number but a string returned from previous query

        else:
            params_ = params_ = {**params_, **{"offset": self.offset}}
            r = self.platform.get(endpoint, params=params_)  # type: ignore

        self.set_airtable_next_offset(r)
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

    def is_last_bulk(self, response, offset=None):
        """
        Determines if is last bulk to fetch.
        """
        if response.get("offset"):
            return False
        else:
            return True

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

    def make_bulk_delete_body(self, bulk_ids):
        """
        Make delete query body from list of IDs

        Airtable DELETE API uses query parameters, not body:
        DELETE /v0/{baseId}/{tableId}?records[]={id1}&records[]={id2}...

        Returns:
            List of IDs to be used as query parameters
        """
        return bulk_ids

    def delete_query(self, body):
        """
        Http call to delete a bulk of items

        Airtable DELETE API expects IDs as query parameters:
        DELETE /v0/{baseId}/{tableId}?records[]={id1}&records[]={id2}...
        """
        self.log("Deleting items")
        # Airtable expects IDs as repeated query parameters: records[]={id}&records[]={id}
        # requests will handle this automatically with a list
        params = {"records[]": body}  # body is the list of IDs
        self.platform.delete(self.delete_endpoint, params=params)  # type: ignore

    ## Note : dealing with options
    ## Note : date normalization only for compare ?

    def get_all_as_df(self, json_normalize=False, modified_after=None):
        """
        Get all items as Pandas.DataFrame, ensuring all schema columns are present even if empty
        """
        # Get the DataFrame using the parent method
        df = super().get_all_as_df(
            json_normalize=json_normalize, modified_after=modified_after
        )

        # If DataFrame is empty, no need to add missing columns
        if len(df) == 0:
            return df

        # Get all column names from the table schema
        try:
            base_schema = self.platform.get(self.schema_endpoint)
            table_schema = [
                table for table in base_schema["tables"] if table["id"] == self.table_id
            ][0]
            all_column_names = [field["name"] for field in table_schema["fields"]]

            # Add missing columns with None values
            missing_columns = []
            for column_name in all_column_names:
                if column_name not in df.columns:
                    df[column_name] = None
                    missing_columns.append(column_name)

            # Log the completion of missing columns
            if missing_columns:
                self.log(
                    f"Added {len(missing_columns)} missing column(s) with None values: {', '.join(missing_columns)}"
                )

        except Exception as e:
            # If schema retrieval fails, log and return DataFrame as-is
            self.log(
                f"Could not retrieve schema to add missing columns: {e}",
                level="warning",
            )

        return df

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
        self.insert(df)
        # raise NotImplementedError("list_children() method not yet implemented")


class AirtableBase(Container):
    PLATFORM_CLASS = AirtablePlatform
    LIST_LEVEL = 1
    CHILD = AirtableTable
    OPTION_SET = OptionSet(
        Container.OPTION_SET.options + [OPT_TYPECAST, OPT_EXTRA_GET_PARAMS]
    )

    platform: RestAPIPlatform

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)
        self.base_id = api_identifier

    def _object_info_impl(self):
        self.platform.get(f"meta/bases/{self.base_id}/tables")  # type: ignore
        return self.make_object_info_response(isOk=True, detail="", name="")

    def create_table_from_schema(
        self, table_name: str, schema: list[Field], relations=False
    ):
        """
        Create an empty table from a schema (list of Tableclone fields)

        Args:
            table_name (str): Name for the new table
            schema (list): List of Fields
            relations (boolean): If true, tableclone will handle relations. If fils, relation fields are treated as text fields.

        Returns:
            Table: Table instance
        """
        super().create_table_from_schema(table_name, schema, relations=relations)
        airtable_fields = []
        for field in schema:
            if field.generic_type != FieldTypes.RELATION or relations:
                airtable_type = self.platform.FIELD_MAPPING.from_generic[
                    field.generic_type
                ]
            else:  # if relation is false we treat relation fields as strings
                airtable_type = self.platform.FIELD_MAPPING.from_generic[
                    FieldTypes.STRING
                ]
            # airtable type if formated as {"type": "xx", "options": {} }
            airtable_field = {**{"name": field.name}, **airtable_type}
            airtable_fields.append(airtable_field)
        json_ = {"name": table_name, "fields": airtable_fields}
        self.log(json_, level="debug")
        r = self.platform.post(  # type: ignore
            f"meta/bases/{self.base_id}/tables",
            json=json_,
        )
        self.log(f"Table created. Airtable response = {r}", level="debug")
        base_id = self.api_identifier
        table_id = r["id"]
        return AirtableTable(r["name"], self.platform, f"{base_id}/{table_id}")  # type: ignore

    def dump_df_to_new_table(self, df, table_name):
        super().dump_df_to_new_table(df, table_name)
        """
        Create a new Airtable table from a DataFrame with all columns typed as text.

        Args:
            df: pandas DataFrame to create table from
            table_name: Name for the new table
        """
        # Create schema with all columns as text fields
        schema = []
        df_with_index = df.reset_index()
        schema = self.platform.table_schema_from_df(df_with_index)

        # Create the table using the schema
        table = self.create_table_from_schema(table_name, schema, relations=False)

        # Re-instanciate the table with typecast = True
        table = AirtableTable(
            table.alias, self.platform, table.api_identifier, options={"typecast": True}
        )  # type: ignore

        # Insert the data into the newly created table
        table.dump_df(df_with_index)
