import sqlite3
from pathlib import Path

import pandas as pd

from ..utils import Option, OptionSet
from .abstracts import (
    Container,
    Field,
    FieldMapper,
    FieldTypes,
    InsertUpdateUpsertTable,
    Platform,
)


class SqlitePlatform(Platform):
    PLATFORM = "sqlite"

    LIST_LEVELS = [0]

    FIELD_MAPPING = FieldMapper(
        {
            "INTEGEG": FieldTypes.INTEGER,
            "REAL": FieldTypes.NUMBER,
            "TEXT": FieldTypes.STRING,
        },
        {
            FieldTypes.INTEGER: "INTEGER",
            FieldTypes.NUMBER: "REAL",
            FieldTypes.STRING: "TEXT",
            FieldTypes.BOOLEAN: "INTEGER",
            FieldTypes.DATE: "TEXT",
            FieldTypes.DATETIME: "TEXT",
            FieldTypes.RELATION: "TEXT",
            FieldTypes.ATTACHMENTS: "TEXT",
        },
    )

    def __init__(self, platform_root_path=None, alias=None, options=None, **kwargs):
        """
        Instantiate a Platform object

        Args:
            platform_root_path(string): Sqlite db path
            secret_string(string): This is ingnored with sqlite
        """
        if not (platform_root_path):
            raise RuntimeError("Sqlite Platform requires platform_root_path")
        super().__init__(platform_root_path=platform_root_path)

    def parse_auth_information(self, secret_string):
        """
        Process secret string or other auth information. Checks that enough information is provided
        and that there are no conflicting information
        """
        self.log("parse_auth_information is not used in sqlite platform", level="debug")

    def sql_query(self, query, paremeters=None):
        """
        Execute a query and fetch the result

        Args:
            query(string): SQL query. May contain positionnal parameters '?'
            parameters(list):  List of values to replace optionnas postional parameters

        Returns:
            List: list of rows
        """
        with sqlite3.connect(Path(self.platform_root_path)) as conn:
            cursor = conn.cursor()
            # Execute the statement
            if paremeters:
                self.log("Sqlite statements with positionals params", level="debug")
                cursor.execute(query, paremeters)
            else:
                cursor.execute(query)
            # Commit the transaction
            try:
                rows = cursor.fetchall()
            except sqlite3.ProgrammingError:
                # This is a statement with no result to fetch such a insert
                rows = []
            conn.commit()
        return rows

    def _list_children_impl(self, level, parent=None):
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """
        raise NotImplementedError("not yet implemented")

    def headers(self):
        """
        Not needed in Postgre table
        """
        raise NotImplementedError(
            "Method headers() is not implemented for Postgre Table and sould not be used"
        )

    def create_object(self, object_name, level, parent=None):
        super().create_object(object_name, level, parent=parent)
        raise NotImplementedError("not yet implemented")


OPT_LAST_MODIFIED_COLUMN = Option(
    "last_modified_column",
    "Column name containing last modification timestamp for filtering records by time",
    str,
)


class SqliteTable(InsertUpdateUpsertTable):
    PLATFORM_CLASS = SqlitePlatform
    BULK_SIZE_INSERT = 100  # Default number of records for bulk queries
    BULK_SIZE_UPDATE = 1  # Default number of records for bulk queries

    UPSERT = False

    OPTION_SET = OptionSet(
        InsertUpdateUpsertTable.OPTION_SET.options + [OPT_LAST_MODIFIED_COLUMN]
    )

    def __init__(
        self,
        alias,
        platform: SqlitePlatform,
        api_identifier,
        options={},
        **kwargs,
    ):
        super().__init__(alias, platform, api_identifier, options=options)
        # Unlike other platforms, there are no "native unique id" as a table may as well be a view or anything
        if self.option_values.get(InsertUpdateUpsertTable.OPT_UNIQUE_ID_COLUMN):
            self.unique_id_column = self.option_values.get(
                InsertUpdateUpsertTable.OPT_UNIQUE_ID_COLUMN
            )
        else:
            raise (
                RuntimeError(
                    "No unique id column provided. SQLite methods requires an unique id column"
                )
            )

        self.last_modified_column = self.option_values.get(OPT_LAST_MODIFIED_COLUMN)

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)
        self.table = self.api_identifier

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        columns = []
        statement = f'PRAGMA table_info("{self.table}")'
        rows = self.platform.sql_query(statement)  # type: ignore
        for row in rows:
            columns.append(row[1])
        return self.make_object_info_response(
            isOk=True, detail="", columns=columns, name="self.api_identifier"
        )

    #########################################
    ############ Get table items ############
    #########################################

    def get_bulk_raw_data(self, offset=None):
        """
        Build query and get raw data for a bulk of items
        """
        raise NotImplementedError(
            "Method get_bulk_raw_data() is not implemented for Postgre Table and sould not be used"
        )

    def bulk_raw_data_to_records(self, response):
        """
        Converts raw data returned by the platform to dict (records style).
        """
        raise NotImplementedError(
            "Method bulk_raw_data_to_records() is not implemented for SQLite Table and sould not be used"
        )

    def is_last_bulk(self, response, offset):
        """
        Determines if is last bulk to fetch.
        """
        raise NotImplementedError(
            "Method is_last_bulk() is not implemented for Postgre Table and sould not be used"
        )

    def get_all(self, modified_after=None):
        """
        Get all items as list of records-like dicts
        """
        # get_all_as_df() does not requirer this method
        raise NotImplementedError(
            "Method get_all() is not implemented for SQLite Table and sould not be used"
        )

    def get_all_as_df(self, json_normalize=False, modified_after=None):
        """
        Get all items a Pandas.DataFrame
        """
        if json_normalize:
            raise NotImplementedError("json_normalize not implemented for SQLite")

        with sqlite3.connect(Path(self.platform.platform_root_path)) as conn:
            sql_query = f'SELECT * FROM "{self.table}"'

            if modified_after:
                if self.last_modified_column:
                    # SQLite datetime comparison using ISO format strings
                    where_stmt = f'WHERE datetime("{self.last_modified_column}") >= datetime(?)'
                    sql_query = sql_query + " " + where_stmt
                    # Pass modified_after as parameter
                    df = pd.read_sql(sql_query, conn, params=[modified_after])
                else:
                    raise RuntimeError(
                        "Can't use modified_after without specifying last_modified_column option"
                    )
            else:
                df = pd.read_sql(sql_query, conn)
        if df[self.unique_id_column].duplicated().any():
            raise IndexError(f"Values of column {self.unique_id_column} are not unique")
        else:
            self.log(f"{self.unique_id_column} is will be used as unique ID")
            df.set_index(self.unique_id_column, inplace=True, drop=False)
            df.index.rename(self.table_index_name(), inplace=True)
            self.log("%s records loaded in loaded in Dataframe" % (len(df)))
            return df

    # TODO: problem if "use native unique ID ??"

    #############################################
    ############ Insert/Update items ############
    #############################################

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row : (value1, value2,...)"""

        statement = (
            "(" + ",".join(["?"] * len(row.index)) + ")"
        )  # We just build a string '(?, ?, ... )'
        parameters = row.tolist()

        self.columns = row.index
        self.comma_sep_columns = ",".join(row.index)  # Needed in make_bulk_insert_body
        return statement, parameters

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        set_clause_list = []
        parameters = []
        for col in row.index:
            if col != self.unique_id_column:
                set_clause_list.append(f"{col} = ?")
                parameters.append(row[col])
        set_stmt = ",".join(set_clause_list)

        where_stmt = f"WHERE {self.unique_id_column} = ?"
        parameters.append(index)

        stmt = f'UPDATE "{self.table}" SET {set_stmt} {where_stmt};'

        return stmt, parameters

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """
        insert_values = []
        insert_params = []
        for statement, parameters in bulk:
            insert_values.append(statement)
            insert_params = insert_params + parameters

        values = ",\n".join(insert_values)

        stmt = (
            f'INSERT INTO "{self.table}" ({self.comma_sep_columns}) VALUES\n {values}'
        )

        return stmt, insert_params  # need to use *args in abstracts

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        update_statements = []
        update_params = []
        for statement, parameters in bulk:
            update_statements.append(statement)
            update_params = update_params + parameters

        return "\n".join(update_statements), update_params

    def insert_query(self, body):
        """
        Http call to insert a bulk of items
        """
        super().insert_query(body)
        # Sqlite sql_query need a tuple to pass positonals query parameters up to
        # platform.sql_query
        self.platform.sql_query(*body)  # type: ignore

    def update_query(self, body):
        """
        Http call to update a bulk of items
        """
        super().update_query(body)
        # Sqlite sql_query need a tuple to pass positonals query parameters up to
        # platform.sql_query
        self.platform.sql_query(*body)  # type: ignore

    def upsert_query(self, body):
        """
        Http call to upsert a bulk of items
        """
        raise NotImplementedError("upsert_query not implemented")

    def make_bulk_delete_body(self, bulk):
        """
        Make delete query body from list of IDs

        Args:
            bulk (list): List of record IDs to delete

        Returns:
            tuple: (SQL statement, parameters list)
        """
        if not bulk:
            return "", []

        # Build placeholders for IN clause: (?, ?, ...)
        placeholders = ",".join(["?"] * len(bulk))
        stmt = f'DELETE FROM "{self.table}" WHERE {self.unique_id_column} IN ({placeholders})'

        return stmt, bulk

    def delete_query(self, body):
        """
        Execute delete query for a bulk of items

        Args:
            body (tuple): (SQL statement, parameters list) from make_bulk_delete_body
        """
        self.log("Deleting items")
        # Pass statement and parameters to platform.sql_query
        self.platform.sql_query(*body)  # type: ignore

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

    def get_table_schema(self):
        """
        returns a list of Tableclone Fields
        """
        raise NotImplementedError(
            "Method get_table_schema() is not yet implemented for SQLite"
        )


class SqliteDB(Container):
    PLATFORM_CLASS = SqlitePlatform

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        self.log("API Identifier is not used on Sqlite DB Container", level="warning")

    def _object_info_impl(self):
        """
        Query the object to fetch informations. Can be used to check that credential is valid.
        This method must return a Dict using self.make_object_info_response()
        """
        statement = "SELECT name FROM sqlite_master WHERE type='table';"
        rows = self.platform.sql_query(statement)  # type: ignore
        self.log(f"SQLite connection OK. {len(rows)} tables found")
        return self.make_object_info_response(
            isOk=True, detail="", name=self.api_identifier
        )

    def dump_df_to_new_table(self, df: pd.DataFrame, table_name):
        """
        Dumps a dataframe to a new Table having Container for parent

        Args:
            df (DataFrame): Dataframe of data to dump
            table_name: Name to be given to newly created table

        Returns:
            Table: New Table object
        """
        super().dump_df_to_new_table(df, table_name)
        with sqlite3.connect(Path(self.platform.platform_root_path)) as conn:
            for column in df.columns:
                if df[column].dtype == "object":
                    df[column] = df[column].astype(str)
            df.to_sql(table_name, conn, if_exists="fail", index=True)

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
        sqlite_field_statements = []
        for field in schema:
            if field.generic_type != FieldTypes.RELATION or relations:
                sqlite_type = SqlitePlatform.FIELD_MAPPING.from_generic[
                    field.generic_type
                ]
            else:  # if relation is false we treat relation fields as strings
                sqlite_type = SqlitePlatform.FIELD_MAPPING.from_generic[
                    FieldTypes.STRING
                ]
            sqlite_field_statements.append(f'"{field.name}" {sqlite_type}')

        joined_field_statement = ", ".join(sqlite_field_statements)
        sqlite_create_statement = (
            f'CREATE TABLE "{table_name}" ({joined_field_statement});'
        )
        self.log(sqlite_create_statement, level="debug")
        print(sqlite_create_statement)
        self.platform.sql_query(sqlite_create_statement)  # type: ignore
        return SqliteTable(table_name, self.platform, table_name)  # type: ignore
