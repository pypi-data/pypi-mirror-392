import pandas as pd
import psycopg2
from psycopg2 import sql

from ..utils import Option, OptionSet
from .abstracts import InsertUpdateUpsertTable, Platform


class PostgrePlatform(Platform):
    PLATFORM = "postgre"

    LIST_LEVELS = [0, 1]

    def __init__(self, platform_root_path=None, secret_string=None, alias=None, options=None):
        """
        Instantiate a Platform object

        Args:
            platform_root_path(string): {url}:{port}/{database}
            secret_string(string): {username}:password
        """
        if not (platform_root_path):
            raise RuntimeError("Postgre Platform requires platform_root_path")
        if not (secret_string):
            raise RuntimeError("Postgre Platform requires secret_string")
        super().__init__(platform_root_path=platform_root_path, secret_string=secret_string)
        (host_port, database) = platform_root_path.split("/")
        (host, port) = host_port.split(":")
        self.host = host
        self.port = port
        self.database = database

    def parse_auth_information(self, secret_string):
        """
        Process secret string or other auth information. Checks that enough information is provided
        and that there are no conflicting information
        """
        super().parse_auth_information(secret_string)
        (username, password) = secret_string.rsplit(":", 1)
        self.username = username
        self.password = password

    def sql_query(self, query):
        """
        Execute a query and fetch the result
        """
        with psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.username,
            password=self.password,
        ) as conn:
            cursor = conn.cursor()
            # Execute the UPDATE statement
            cursor.execute(query)
            # Commit the transaction
            try:
                rows = cursor.fetchall()
            except psycopg2.ProgrammingError as e:
                # This is a statement with no result to fetch such a insert
                rows = []
            conn.commit()
        return rows

    def _list_children_impl(self, level, parent=None):
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """
        if level == 0:
            # Fetching schema list
            schemas_list = []
            self.log("Querying schema list")
            statement = "SELECT schema_name FROM information_schema.schemata"
            rows = self.sql_query(statement)
            for row in rows:
                # ID and name is the same
                schemas_list.append({"id": row[0], "name": row[0]})
            self.log("Schemas:  %s" % (schemas_list))
            return self._make_list_response(schemas_list)

        elif level == 1:
            # Fetching table list
            tables_list = []
            self.log("Querying table list for schema %s" % (parent))
            statement = (
                f"SELECT table_name FROM information_schema.tables WHERE table_schema='{parent}'"
            )
            rows = self.sql_query(statement)
            for row in rows:
                tables_list.append({"id": row[0], "name": row[0]})
            self.log("Tables:  %s" % (tables_list))
            return self._make_list_response(tables_list)
        else:
            raise IndexError("Meta level %s not supported in %s" % (level, self.platform))

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


class PostgreTable(InsertUpdateUpsertTable):
    PLATFORM_CLASS = PostgrePlatform

    BULK_SIZE_INSERT = 100  # Default number of records for bulk queries
    BULK_SIZE_UPDATE = 100  # Default number of records for bulk queries
    BULK_SIZE_UPSERT = 100

    UPSERT = False  # UPSERT for Pg require unicity constraint on the DB. Need a frontend option to disable UPSERT before passing to True.

    OPTION_SET = OptionSet(
        InsertUpdateUpsertTable.OPTION_SET.options + [OPT_LAST_MODIFIED_COLUMN]
    )

    def __init__(
        self,
        alias,
        platform: PostgrePlatform,
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
                    "No unique id column provided. PostgreSQL methods requires an unique id column"
                )
            )

        self.last_modified_column = self.option_values.get(OPT_LAST_MODIFIED_COLUMN)

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)
        (schema, table) = self.api_identifier.split(".")
        self.schema = schema
        self.table = table

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        columns = []
        statement = f"SELECT column_name FROM information_schema.columns WHERE table_schema='{self.schema}' AND table_name='{self.table}'"
        rows = self.platform.sql_query(statement)
        for row in rows:
            columns.append(row[0])
        return self.make_object_info_response(
            isOk=True, detail="", columns=columns, name="self.api_identifier"
        )

    #########################################
    ############ Get table items ############
    #########################################

    def get_table_schema(self):
        """
        returns a list of Tableclone Fields
        """
        raise NotImplementedError("Method get_table_schema() is not yet implemented for Postgre")

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
        Dict must contain a key named as DATAFRAME_INDEX_NAME
        """
        raise NotImplementedError(
            "Method bulk_raw_data_to_records() is not implemented for Postgre Table and sould not be used"
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
            "Method get_all() is not implemented for PostgreSQL Table and sould not be used"
        )

    def get_all_as_df(self, json_normalize=False, modified_after=None):
        """
        Get all items a Pandas.DataFrame
        """
        if json_normalize:
            raise NotImplementedError("json_normalize not implemented for PostgreSQL")

        with psycopg2.connect(
            host=self.platform.host,
            port=self.platform.port,
            database=self.platform.database,
            user=self.platform.username,
            password=self.platform.password,
        ) as conn:
            sql_query = sql.SQL("SELECT * FROM {}.{}").format(
                sql.Identifier(self.schema), sql.Identifier(self.table)
            )

            if modified_after:
                if self.last_modified_column:
                    where_stmt = sql.SQL(
                        "WHERE {}::timestamp with time zone >= {}::timestamp with time zone"
                    ).format(
                        sql.Identifier(self.last_modified_column),
                        sql.Literal(modified_after),
                    )

                    sql_query = sql.SQL("{query} {where}").format(
                        query=sql_query,
                        where=where_stmt,
                    )

                else:
                    raise RuntimeError(
                        "Can't use modified_after without specifying last_modified_column option"
                    )
            df = pd.read_sql(sql_query.as_string(conn), conn)
        if df[self.unique_id_column].duplicated().any():
            raise IndexError(f"Values of column {self.unique_id_column} are not unique")
        else:
            self.log(f"{self.unique_id_column} is will be used as unique ID")
            df.index = df[self.unique_id_column]
            df.index.rename(self.table_index_name(), inplace=True)
            self.log("%s records loaded in loaded in Dataframe" % (len(df)))
            return df

    # TODO: problem if "use native unique ID ??"

    #############################################
    ############ Insert/Update items ############
    #############################################

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row : (value1, value2,...)"""
        sql_values = []
        parameter_placeholders = []
        for col in row.index:
            if row[col] is None:
                value = sql.SQL("NULL")
            else:
                value = sql.Literal(row[col])
            sql_values.append(value)
        comma_sep_values = sql.SQL(",").join(sql_values)
        self.columns = row.index
        self.comma_sep_columns = sql.SQL(",").join(
            [sql.Identifier(column_name) for column_name in row.index]
        )  # Needed in make_bulk_insert_body
        return sql.SQL("({})").format(comma_sep_values)

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        set_clause_list = []
        for col in row.index:
            if col != self.unique_id_column:
                if row[col] is None:
                    set_clause = sql.SQL("{} = NULL").format(sql.Identifier(col))
                    # NOTE : Probably useless : sql.Literal(None) should return NULL
                else:
                    set_clause = sql.SQL("{} = {}").format(
                        sql.Identifier(col), sql.Literal(row[col])
                    )
                set_clause_list.append(set_clause)
        set_stmt = sql.SQL(",").join(set_clause_list)

        where_stmt = sql.SQL("WHERE {} = {}").format(
            sql.Identifier(self.unique_id_column), sql.Literal(index)
        )
        stmt = sql.SQL("UPDATE {schema}.{table} SET {set_stmt} {where_stmt};").format(
            schema=sql.Identifier(self.schema),
            table=sql.Identifier(self.table),
            set_stmt=set_stmt,
            where_stmt=where_stmt,
        )
        return stmt

    def make_record_upsert_from_df_row(self, row):
        return self.make_record_insert_from_df_row(row)

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """
        stmt = sql.SQL(
            "INSERT INTO {schema}.{table} ({comma_sep_columns}) VALUES\n {values};"
        ).format(
            schema=sql.Identifier(self.schema),
            table=sql.Identifier(self.table),
            comma_sep_columns=self.comma_sep_columns,  # previously SQL formatted
            values=sql.SQL(",\n").join(bulk),
        )

        return stmt

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        return sql.SQL("\n").join(bulk)

    def make_bulk_upsert_body(self, bulk, unique_id_column):
        """
        Make upsert query body from list of records
        """
        stmt = sql.SQL(
            "INSERT INTO {schema}.{table} ({comma_sep_columns}) VALUES\n {values} ON CONFLICT ({unique_id_column}) DO UPDATE SET "
        ).format(
            schema=sql.Identifier(self.schema),
            table=sql.Identifier(self.table),
            comma_sep_columns=self.comma_sep_columns,  # previously SQL formatted
            values=sql.SQL(",\n").join(bulk),
            unique_id_column=sql.Identifier(unique_id_column),
        )

        update_columns = [
            sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(column), sql.Identifier(column))
            for column in self.columns
            if column != unique_id_column
        ]
        update_stmt = sql.SQL(", ").join(update_columns)

        return stmt + update_stmt + sql.SQL(";")

    def insert_query(self, body):
        """
        Http call to insert a bulk of items
        """
        super().insert_query(body)
        self.platform.sql_query(body)

    def update_query(self, body):
        """
        Http call to update a bulk of items
        """
        super().update_query(body)
        self.platform.sql_query(body)

    def upsert_query(self, body):
        """
        Http call to update a bulk of items
        """
        super().upsert_query(body)
        self.platform.sql_query(body)

    def make_bulk_delete_body(self, bulk):
        """
        Make delete query body from list of IDs

        Args:
            bulk (list): List of record IDs to delete

        Returns:
            psycopg2.sql.Composed: SQL delete statement with IN clause
        """
        if not bulk:
            return sql.SQL("")

        # Build list of literals for IN clause
        id_literals = [sql.Literal(record_id) for record_id in bulk]
        in_clause = sql.SQL(",").join(id_literals)

        stmt = sql.SQL("DELETE FROM {schema}.{table} WHERE {unique_id_column} IN ({ids});").format(
            schema=sql.Identifier(self.schema),
            table=sql.Identifier(self.table),
            unique_id_column=sql.Identifier(self.unique_id_column),
            ids=in_clause,
        )

        return stmt

    def delete_query(self, body):
        """
        Execute delete query for a bulk of items

        Args:
            body (psycopg2.sql.Composed): SQL statement from make_bulk_delete_body
        """
        self.log("Deleting items")
        self.platform.sql_query(body)

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
