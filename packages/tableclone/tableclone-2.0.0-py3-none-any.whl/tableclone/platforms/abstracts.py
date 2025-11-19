import time
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import requests

from ..utils import (
    Option,
    OptionSet,
    OptionValues,
    create_columns_if_not_exists,
    get_logger,
)


class Field(ABC):
    def __init__(
        self, platform: "Platform", field_name, field_specific_type, reference=None
    ):
        self.platform = platform
        self.name = field_name
        self.specific_type = field_specific_type
        self.reference = reference
        try:
            self.generic_type = platform.FIELD_MAPPING.to_generic[field_specific_type]
        except IndexError:
            raise IndexError(
                f'Can\'t map field type "{field_specific_type}" to generic type'
            )

    def __str__(self):
        relation_str = f" -> {self.reference}" if self.reference else ""
        return f"{self.name} ({self.specific_type}|{self.generic_type}{relation_str})"


class FieldTypes:
    STRING = "str"
    INTEGER = "int"
    NUMBER = "float"
    BOOLEAN = "bool"
    DATE = "date"
    DATETIME = "datetime"
    RELATION = "relation"
    ATTACHMENTS = "attachments"


class FieldMapper:
    def __init__(self, to_generic_mapping: dict, from_generic_mapping: dict):
        self.to_generic = to_generic_mapping
        self.from_generic = from_generic_mapping


class Platform(ABC):
    PLATFORM = ""  # Platform name (for logs, etc.)
    LIST_LEVELS = [0]
    FIELD_MAPPING = FieldMapper({}, {})

    OPTION_SET = OptionSet([])  # Empty option set

    def __init__(self, platform_root_path="", secret_string=None, options={}):
        """
        Instantiate a Platform object.

        Args:
            platform_root_path (string): Base URL if needed (if custom domain). Example:
                                    - Bubble: https://{app url}/api/1.1/obj
                                    - Airtalbe: Not needed (because always https://api.airtable.com/v0)
            secret_string (string): All platforme mest be instanciable providing a single string for auth information
                                    (can be API Key, JWT toket, BasicAuth encoded, username:password, ...).
                                    Children class may have other way of providing auth information.
            options (dict):

        Returns:
            Platform: Platform instance
        """
        self.logger = get_logger(self.__class__.__name__)
        self.platform_root_path = platform_root_path
        self.secret_string = secret_string  # Store original secret for reuse in configs
        self.parse_auth_information(secret_string)
        self.log(f"Options: {options}")
        self.option_values = OptionValues(
            self.OPTION_SET, options
        )  # this validates the option values

    def table_schema_from_df(self, df):
        """Infer table schema from a pandas DataFrame by analyzing column data types.

        Args:
            df: pandas DataFrame to analyze

        Returns:
            list[Field]: List of Field objects representing the inferred schema
        """
        schema = []
        for col_name, col_serie in df.items():
            if pd.api.types.is_integer_dtype(col_serie.dropna()):
                generic_type = FieldTypes.INTEGER
            elif pd.api.types.is_float_dtype(col_serie.dropna()):
                generic_type = FieldTypes.NUMBER
            elif pd.api.types.is_bool_dtype(col_serie.dropna()):
                generic_type = FieldTypes.BOOLEAN
            else:
                generic_type = FieldTypes.STRING

            field = Field(
                platform=self,
                field_name=col_name,
                field_specific_type=self.FIELD_MAPPING.from_generic[generic_type][
                    "type"
                ],
            )
            schema.append(field)
        return schema

    def __str__(self):
        return f"[{self.PLATFORM}]"

    def log(self, message, level="info"):
        formated_msg = f"{str(self)} {message}"

        getattr(self.logger, level)(formated_msg)

    @abstractmethod
    def parse_auth_information(self, secret_string):
        """
        Process secret string or other auth information. Checks that enough information is provided
        and that there are no conflicting information
        """
        self.log("Processing auth information")
        pass

    ####################################################
    ############ Generic platform interface ############
    ####################################################

    def list_children(self, level, parent=None) -> list[dict]:
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """
        self.log("Listing level %s" % (level))
        if level not in self.LIST_LEVELS:
            raise IndexError(f"Meta level {level} not supported in {self}")
        else:
            return self._make_list_response(
                self._list_children_impl(level, parent=parent)
            )

    @abstractmethod
    def _list_children_impl(self, level, parent=None) -> list[dict] | None:
        pass

    def _make_list_response(self, list: list[dict] | None) -> list[dict]:
        """
        Response should be a list of dict {"id" :  ,"name": }. This function both
        checks format of list is appropriate and filters any other propertes.
        Response is aimed to be used in http response for cloud function
        """
        self.log(list, level="debug")
        if list:
            return [{"id": item["id"], "name": item["name"]} for item in list]
        else:
            return []

    @abstractmethod
    def create_object(self, object_name, level, parent=None):
        """
        Create a new object (Table, Database...) depending on level.
        """
        self.log(f"Creating a new object (level {level} having parent {parent})")


class RestAPIPlatform(Platform):
    API_SLEEP_TIME = 0

    @abstractmethod
    def headers(self) -> dict:
        """
        Returns headers with auth
        """
        pass

    def _handle_http_error(self, response):
        """
        Handle HTTP errors by including response details in exception.

        This method provides detailed error information from API responses,
        which is especially useful for debugging issues like invalid field values.

        Args:
            response: requests.Response object

        Raises:
            HTTPError with detailed error message including response body
        """
        import json
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Try to get JSON error details from response
            try:
                error_details = response.json()
                error_msg = f"{e}\n\nResponse details:\n{json.dumps(error_details, indent=2)}"
            except Exception:
                # Fallback to text if JSON parsing fails
                error_msg = f"{e}\n\nResponse text:\n{response.text[:500]}"  # Limit to 500 chars

            self.log(f"HTTP Error: {error_msg}", level="error")
            raise requests.exceptions.HTTPError(error_msg, response=response) from e

    def get(self, endpoint=None, **kwargs):
        """
        Returns parsed response JSON
        """
        url = (
            self.platform_root_path + "/" + endpoint
            if endpoint
            else self.platform_root_path
        )
        r = requests.get(url, headers=self.headers(), **kwargs)
        self._handle_http_error(r)
        time.sleep(self.API_SLEEP_TIME)

        return r.json()

    def post(self, endpoint=None, extra_headers=None, **kwargs):
        url = (
            self.platform_root_path + "/" + endpoint
            if endpoint
            else self.platform_root_path
        )

        headers_ = self.headers()
        if extra_headers:
            headers_.update(extra_headers)
        r = requests.post(url, headers=headers_, **kwargs)
        self._handle_http_error(r)
        time.sleep(self.API_SLEEP_TIME)
        return r.json()

    def patch(self, endpoint=None, **kwargs):
        url = (
            self.platform_root_path + "/" + endpoint
            if endpoint
            else self.platform_root_path
        )
        r = requests.patch(
            url,
            headers=self.headers(),
            **kwargs,
        )
        self._handle_http_error(r)
        time.sleep(self.API_SLEEP_TIME)
        return r.json()

    def delete(self, endpoint=None, **kwargs):
        """
        Performs DELETE HTTP request

        Args:
            endpoint: API endpoint path (appended to platform_root_path)
            **kwargs: Additional arguments passed to requests.delete()

        Returns:
            Response JSON if available, None otherwise
        """
        url = (
            self.platform_root_path + "/" + endpoint
            if endpoint
            else self.platform_root_path
        )
        r = requests.delete(url, headers=self.headers(), **kwargs)
        self._handle_http_error(r)
        time.sleep(self.API_SLEEP_TIME)
        return r.json() if r.text else None


class PlatformObject(ABC):
    PLATFORM_CLASS = Platform

    OPTION_SET = OptionSet([])  # Empty option set

    def __init__(
        self,
        alias: str,
        platform: Platform | dict,
        api_identifier=None,
        options={},
        check=True,
    ):
        """
        Either Table or Container

        Args:
            alias (string): Alias to be used in logs etc.
            platform (Platform | dict): Either a Platform instance or a dict of kwargs to create a Platform instance
            api_identifier (string): ID of the object. Can be None, for sqlite DB container for example
            options (dict): Options passed to the object
            check (boolean): If True, will call object_info to check object is valid (e.g. API call is correct)

        Returns:
            Object: PlatformObject instance
        """
        self.logger = get_logger(self.__class__.__name__)
        self.alias = (
            alias if alias else api_identifier
        )  # If no alias we use API ID as alias
        self.api_identifier = api_identifier

        # Platform is given as a Platform instance or dict
        if isinstance(platform, self.PLATFORM_CLASS):
            self.platform = platform
        elif type(platform) is dict:
            self.platform = self.PLATFORM_CLASS(**platform)  # type: ignore
        else:
            raise (
                RuntimeError(f"Unproccessable platform: {type(platform)},  {platform}")
            )
        self.log(f"Options: {options}")
        self.option_values = OptionValues(
            self.OPTION_SET, options
        )  # this validates the option values

        if api_identifier:
            self.parse_api_identifier(api_identifier)
        if check:
            info = self.object_info()

            if info["isOk"] is False:
                raise RuntimeError(f"object_info returned an error: {info['detail']}")

    def __str__(self):
        return f"{self.platform} ({self.alias})"

    def log(self, message, level="info"):
        formated_msg = f"{str(self)} {message}"

        getattr(self.logger, level)(formated_msg)

    @abstractmethod
    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        self.log(f"Parsing api_identifier : {api_identifier}", level="info")

    def object_info(self) -> dict:
        """
        Query the object to fetch informations. Can be used to check that credential is valid.
        In case of error, the error is returned
        """
        self.log("Querying object_info.")
        try:
            return self._object_info_impl()

        # in case of unhandled exception, we return error information in the response
        except Exception as e:
            return self.make_object_info_response(
                isOk=False,
                detail=e.__class__.__name__ + " - " + str(e),
                name="",
            )

    @abstractmethod
    def _object_info_impl(self) -> dict:
        """
        Query the object to fetch informations. Can be used to check that credential is valid.
        To normalize response, this method must return a Dict using self.make_object_info_response()
        """
        pass

    def make_object_info_response(self, **kwargs):
        """
        Ensure the response format is the same among child classes.
        Response is aimed to be used in http response for cloud function.
        Expected kwargs are:
            isOk (bool): True if Tableclone could fetch the object, else False
            detail (str): If False, error detail
            name (str): Name of the object on the platform
        """
        response = {
            "isOk": kwargs.get(
                "isOk"
            ),  # True if Tableclone could fetch the object, else False
            "detail": kwargs.get("detail"),  # If False, error detail
            "name": kwargs.get("name"),  # Name of the object on the platform
        }

        self.log(f"object_info: {response}", level="debug")
        return response

    def to_config(self):
        """
        Export current object configuration as JSON-serializable dict.

        Returns config structure ready for TaskInterface or CLI.
        Useful for generating configs from existing Table instances.

        Returns:
            dict: Config structure with platform, alias, api_identifier, and options
        """
        config = {
            "alias": self.alias,
            "api_identifier": self.api_identifier,
            "platform": {
                "platform_root_path": self.platform.platform_root_path,
                "options": self.platform.option_values.values.copy(),
            },
            "options": self.option_values.values.copy(),
        }

        # Add secret if present (stored since Platform.__init__ line 79)
        if hasattr(self.platform, "secret_string") and self.platform.secret_string:
            config["platform"]["secret_string"] = self.platform.secret_string

        return config

    def with_options(self, **new_options):
        """
        Create new instance with merged options (immutable pattern).

        Allows creating variants of a PlatformObject with different options without
        mutating the original object. Useful for reusing fixtures in tests with
        different configurations.

        Example:
            base_table = sqlite_with_sample_data  # Fixture
            filtered = base_table.with_options(allowed_columns=["id", "name"])

        Args:
            **new_options: Keyword arguments for options to add or override

        Returns:
            PlatformObject: New instance with merged options
        """
        merged_options = {**self.option_values.values, **new_options}
        return self.__class__(
            alias=self.alias,
            platform=self.platform,
            api_identifier=self.api_identifier,
            options=merged_options,
            check=False,  # Skip object_info check (already validated)
        )


class Table(PlatformObject):
    OPT_ALLOWED_COLUMNS = Option(
        "allowed_columns",
        "Limit tableclone to these columns only",
        list,
        default_value=[],
    )
    OPT_UNIQUE_ID_COLUMN = Option(
        "unique_id_column",
        "For platforms that don't have a native unique ID, this column will be used as unique ID (e.g. PostgreSQL, SQLite...)",
        str,
    )
    OPT_OVERRIDE_NATIVE_ID_NAME = Option(
        "override_native_id_name",
        "Column name for the native unique identifier column. It can be usefull to override the default value when it conflicts with existing column names",
        str,
    )
    OPTION_SET = OptionSet(
        [OPT_ALLOWED_COLUMNS, OPT_UNIQUE_ID_COLUMN, OPT_OVERRIDE_NATIVE_ID_NAME]
    )

    UPSERT = False

    NATIVE_ID_NAME = (
        "id_tblcln"  # How native unique ID should be named (ex : record_id in Airtable)
    )

    def __init__(
        self,
        alias,
        platform: Platform | dict,
        api_identifier,
        options={},
        check=True,
        **kwargs,
    ):
        super().__init__(alias, platform, api_identifier, options=options, check=check)

        self.unique_id_column = self.option_values.get(Table.OPT_UNIQUE_ID_COLUMN)
        self.allowed_columns = self.option_values.get(Table.OPT_ALLOWED_COLUMNS)

        self.log("Table object instanciated")

    def make_object_info_response(self, **kwargs):
        """
        Response is aimed to be used in http response for cloud function
        Expected kwargs are: isOk (bool), detail (str), columns (list), name (str)"""
        response = {
            "isOk": kwargs.get(
                "isOk"
            ),  # True if Tableclone could fetch the object, else False
            "detail": kwargs.get("detail"),  # If False, error detail
            "columns": kwargs.get("columns"),  # List of columns
            "name": kwargs.get("name"),  # Name of the object on the platform
        }

        self.log(f"object_info: {response}", level="debug")
        return response

    #########################################
    ############ Get table items ############
    #########################################

    def table_index_name(self):
        """
        Returns the name of the unique ID to be used to name indexes
        """
        if self.option_values.get(Table.OPT_OVERRIDE_NATIVE_ID_NAME):
            return self.option_values.get(Table.OPT_OVERRIDE_NATIVE_ID_NAME)
        # else we prefix with tc_ to avoid conflicts between index name and column name
        elif self.option_values.get(Table.OPT_UNIQUE_ID_COLUMN):
            return f"tc_{self.option_values.get(Table.OPT_UNIQUE_ID_COLUMN)}"
        else:
            return f"tc_{self.NATIVE_ID_NAME}"

    @abstractmethod
    def get_table_schema(self) -> list["Field"]:
        """
        returns a list of Tableclone Fields
        """
        self.log("Fetching table schema")
        pass

    @abstractmethod
    def get_all(self, modified_after=None) -> list:
        pass

    def get_all_as_df(self, json_normalize=False, modified_after=None) -> pd.DataFrame:
        """
        Get all items a Pandas.DataFrame
        """
        if json_normalize:
            df = pd.json_normalize(self.get_all(modified_after=modified_after))
            self.log("Normalizing potentiel nested json")
        else:
            df = pd.DataFrame(self.get_all(modified_after=modified_after))
        if len(df) > 0:
            df = df.set_index(self.table_index_name(), drop=True)
        df.index.rename(self.table_index_name(), inplace=True)  # works for empty df
        return df

    def date_normalize(self, df, sample_size=200):
        """
        Date format may differ among platforms (with or without timezone, ISO format or other format, precision, etc.)
        This function propose a normalization in order to compare different Tables'df
        """
        # Converting compatible columns to datetime(UTC), then round to sec, then back to str
        date_patterns = [
            r".*\d{4}-\d{2}-\d{2}.*",
            r".*\d{2}/\d{2}/\d{4}.*",
            r".*\d{4}/\d{2}/\d{2}.*",
        ]

        # Converting compatible columns to datetime(UTC), then round to sec, then back to str
        for col in df.columns:
            if df[col].dtype == "object":
                self.log(f"Testing if column {col} is a datetime data", level="debug")
                sample = df[col].dropna()
                # If only NA, we don't wan to convert to datetime
                if len(sample) == 0:
                    continue
                # Timestamps are usualy less than 30 characters, so if there is a value with more than 30 chars we pass
                if (sample.astype(str).str.len() > 30).any():
                    continue
                sample = sample.sample(min(sample_size, len(sample)))
                # Narrowing date possible match with regex to avoid converting float or numbers to date
                if not any(
                    sample.astype(str).str.contains(pat).any() for pat in date_patterns
                ):
                    continue
                try:
                    pd.to_datetime(sample, utc=True)
                    df[col] = (
                        pd.to_datetime(df[col], utc=True)
                        .dt.round("s")
                        .astype(str)
                        .replace(
                            {"NaT": None}
                        )  # because pd.NaT have been converted to str 'NaT'
                    )
                    self.log(
                        f"Column {col} has been identified as Date type and has been normalized"
                    )
                except (ValueError, TypeError, AttributeError):
                    pass

    def sanitize_df(self, df, date_normalize=False) -> pd.DataFrame:
        create_columns_if_not_exists(df, self.allowed_columns)
        # Filter and reorder on Table columns list
        # columns = [col for col in self.allowed_columns if col in df.columns.tolist()]
        if self.allowed_columns:
            df = df[self.allowed_columns]

        # Filling NaN with None for JSON compliancy.
        self.log("Sanitazing data")
        df = df.replace({np.nan: None})

        if date_normalize:
            self.date_normalize(df)
        return df

    def get_sanitized_df(
        self, date_normalize=False, modified_after=None
    ) -> pd.DataFrame:
        """
        Uses allowed_columns to filter / reorder the DataFrame
        Sanitize DataFrame for general API compatibility: replace np.nan by None
        """
        df = self.get_all_as_df(modified_after=modified_after)
        self.log(f"{len(df)} records loaded")

        df = self.sanitize_df(df, date_normalize=date_normalize)
        # self.log(df.dtypes, level="debug")
        if df.index.duplicated().any():
            raise IndexError(f"Duplicated index for {self}")
        return df

    #############################################
    ############ Insert/Update items ############
    #############################################

    @abstractmethod
    def dump_df(self, df):
        """
        Dumps a dataframe to an existing Table, preserves ID, deletes all data and repopulate with new data

        Args:
            df (DataFrame): Dataframe of data to dump

        Returns:
            str: New table API Identifier
        """
        self.log("Dumping dataframe to current table")

    def list_columns(self):
        """
        Returns a list of allowed columns for this table (that is all colums minus columns masked with option OPT_ALLOWED_COLUMNS)
        """
        if not self.option_values.get(Table.OPT_ALLOWED_COLUMNS):
            return self.object_info()["columns"]
        else:
            return self.option_values.get(Table.OPT_ALLOWED_COLUMNS)

    def auto_map(self, destination: "Table"):
        """
        Generates a mapping (columns) self -> destination based on columns names.
        """
        src_columns = self.list_columns() or []
        dst_columns = destination.list_columns()

        mapping = {}
        for src_col in src_columns:
            # src_col in destination columns (AND masks unless masks are not provided)
            if (
                src_col in dst_columns
                and src_col != self.unique_id_column
                and src_col != destination.unique_id_column
            ):
                mapping.update({src_col: src_col})
        self.log(f"Mapping generated by matching source and destination : {mapping}")
        return mapping


class PaginatedTable(Table):
    OFFSET_MODE_VALUE_PAGE = "page"
    OFFSET_MODE_VALUE_RECORDS = "records"  # default
    # Default paging mode is "record offset". Some platforms requires
    # paging offset. see get_all()
    offset_mode = OFFSET_MODE_VALUE_RECORDS
    BULK_SIZE_GET = 100

    @abstractmethod
    def get_bulk_raw_data(self, offset=0, modified_after=None):
        """
        Build query and get raw data for a bulk of items
        """
        self.log(
            f"Getting bulk of data, offset {offset} (offset_mode: {self.offset_mode}, modified_after: {modified_after})"
        )
        pass

    @abstractmethod
    def bulk_raw_data_to_records(self, response) -> list[dict]:
        """
        Converts raw data returned by the platform to dict (records style).
        Dict must contain a key named as self.table_index_name()
        """
        self.log(f"Parsing response : {response}", level="debug")
        pass

    @abstractmethod
    def is_last_bulk(self, response, offset) -> bool:
        """
        Determines if is last bulk to fetch.
        """
        pass

    def get_all(self, modified_after=None):
        """
        Get all items as list of records-like dicts
        """
        self.log(f"Fetchnig all records modified after {modified_after}")
        values = []
        offset = 0
        response = self.get_bulk_raw_data(offset, modified_after=modified_after)
        bulk_values = self.bulk_raw_data_to_records(response)
        is_last_ = self.is_last_bulk(response, offset)
        values = values + bulk_values
        while not is_last_:
            # time.sleep(self.platform.API_SLEEP_TIME)
            if self.offset_mode == PaginatedTable.OFFSET_MODE_VALUE_RECORDS:
                offset += self.BULK_SIZE_GET
            elif self.offset_mode == PaginatedTable.OFFSET_MODE_VALUE_PAGE:
                offset += 1
            else:
                raise ValueError(f"Incorect offset_mode for {self}")
            response = self.get_bulk_raw_data(offset, modified_after=modified_after)
            bulk_values = self.bulk_raw_data_to_records(response)
            is_last_ = self.is_last_bulk(response, offset)
            values = values + bulk_values
        return values


class InsertUpdateUpsertTable(Table):
    BULK_SIZE_INSERT = 10  # Default number of records for bulk queries
    BULK_SIZE_UPDATE = 10  # Default number of records for bulk queries
    BULK_SIZE_UPSERT = 10  # Default number of records for bulk queries
    BULK_SIZE_DELETE = 10  # Default number of records for bulk queries

    def make_record_insert_from_df_row(self, row):
        """Make a record for insert queries frome a DataFrame row"""
        raise NotImplementedError(
            "make_record_insert_from_df_row method not implemented"
        )

    def make_record_update_from_df_row(self, index, row):
        """Make a record for update queries frome a DataFrame row"""
        raise NotImplementedError(
            "make_record_update_from_df_row method not implemented"
        )

    def make_record_upsert_from_df_row(self, row):
        """Make a record for update queries frome a DataFrame row"""
        raise NotImplementedError(
            "make_record_upsert_from_df_row method not implemented"
        )

    def iter_bulk_insert(self, df):
        """
        Iterates a DataFrame of Table data returning bulks of Platform.BULK_SIZE_INSERT
        records
        """
        # Slicing by group of XX to call bulk
        for i in range(0, len(df), self.BULK_SIZE_INSERT):
            records = []
            for index, row in df.iloc[
                i : min(i + self.BULK_SIZE_INSERT, len(df)), :
            ].iterrows():
                records.append(self.make_record_insert_from_df_row(row))
            yield records

    def iter_bulk_update(self, df):
        """
        Iterates a DataFrame of Table data returning bulks of Platform.BULK_SIZE_UPDATE
        records
        """
        # Slicing by group of XX to call bulk
        for i in range(0, len(df), self.BULK_SIZE_UPDATE):
            records = []
            for index, row in df.iloc[
                i : min(i + self.BULK_SIZE_UPDATE, len(df)), :
            ].iterrows():
                records.append(self.make_record_update_from_df_row(index, row))
            yield records

    def iter_bulk_upsert(self, df):
        """
        Iterates a DataFrame of Table data returning bulks of Platform.BULK_SIZE_UPSERT
        records
        """
        # Slicing by group of XX to call bulk
        for i in range(0, len(df), self.BULK_SIZE_UPSERT):
            records = []
            for index, row in df.iloc[
                i : min(i + self.BULK_SIZE_UPSERT, len(df)), :
            ].iterrows():
                records.append(self.make_record_upsert_from_df_row(row))
            yield records

    def iter_bulk_delete(self, ids):
        """
        Iterates a list of IDs returning bulks of Platform.BULK_SIZE_DELETE IDs

        Args:
            ids: List of IDs to delete (in table_index_name() format)

        Yields:
            List of IDs (bulk)
        """
        for i in range(0, len(ids), self.BULK_SIZE_DELETE):
            yield ids[i : min(i + self.BULK_SIZE_DELETE, len(ids))]

    def make_bulk_insert_body(self, bulk):
        """
        Make insert query body from list of records
        """
        raise NotImplementedError("make_bulk_insert_body method not implemented")

    def make_bulk_update_body(self, bulk):
        """
        Make update query body from list of records
        """
        raise NotImplementedError("make_bulk_update_body method not implemented")

    def make_bulk_upsert_body(self, bulk, unique_id_column):
        """
        Make upsert query body from list of records
        """
        # Overwrite in child function
        raise NotImplementedError("make_bulk_upsert_body method not implemented")

    def make_bulk_delete_body(self, bulk_ids):
        """
        Make delete query body from list of IDs

        Args:
            bulk_ids: List of IDs to delete (in table_index_name() format)

        Returns:
            Request body for delete operation (platform-specific)
        """
        raise NotImplementedError("make_bulk_delete_body method not implemented")

    @abstractmethod
    def insert_query(self, body):
        """
        Http call to insert a bulk of items
        """
        self.log("Inserting items")

    @abstractmethod
    def update_query(self, body):
        """
        Http call to update a bulk of items
        """
        self.log("Updating items")

    @abstractmethod
    def upsert_query(self, body):
        """
        Http call to upsert a bulk of items
        """
        self.log("Upserting items")

    def delete_query(self, body):
        """
        Http call to delete a bulk of items

        Args:
            body: Request body for delete operation (platform-specific)
        """
        self.log("Deleting items")
        raise NotImplementedError("delete_query method not implemented")

    def insert(self, df):
        """
        Create new records based on a dataframe. DataFrame should be indexed with
        platform Unique ID and column names sould match with table's columns
        """
        self.log("Creating %s new items in Table %s" % (len(df), self))
        for bulk in self.iter_bulk_insert(self.sanitize_df(df)):
            body_ = self.make_bulk_insert_body(bulk)
            self.log("INSERT DATA\n" + str(body_), level="debug")
            self.insert_query(body_)

    def update(self, df):
        """
        Update existing records based on a dataframe. DataFrame should be indexed with
        platform Unique ID and column names sould match with table's columns
        """
        self.log("Updating %s items in Table %s" % (len(df), self))
        for bulk in self.iter_bulk_update(self.sanitize_df(df)):
            body_ = self.make_bulk_update_body(bulk)
            self.log("UPDATE DATA\n" + str(body_), level="debug")
            self.update_query(body_)

    def upsert(self, df, unique_id_column):
        """
        Create new records based on a dataframe. DataFrame should be indexed with
        platform Unique ID and column names sould match with table's columns
        """
        self.log("Upserting %s new items in Table %s" % (len(df), self))
        for bulk in self.iter_bulk_upsert(self.sanitize_df(df)):
            body_ = self.make_bulk_upsert_body(bulk, unique_id_column)
            self.log("UPSERT DATA\n" + str(body_), level="debug")
            self.upsert_query(body_)

    def delete(self, ids):
        """
        Delete records by their IDs

        Args:
            ids: List of IDs to delete (in table_index_name() format)
                 Can be a list of strings or extracted from DataFrame index
        """
        # Convert to list if needed (in case it's a pandas Index or Series)
        if not isinstance(ids, list):
            ids = list(ids)

        self.log("Deleting %s items from Table %s" % (len(ids), self))
        for bulk_ids in self.iter_bulk_delete(ids):
            body_ = self.make_bulk_delete_body(bulk_ids)
            self.log("DELETE DATA\n" + str(body_), level="debug")
            self.delete_query(body_)


class Container(PlatformObject):
    LIST_LEVEL = 0  # To use platform.list
    CHILD = Table  # Update with child class

    def __init__(
        self,
        alias,
        platform: Platform,
        api_identifier,
        options=None,
        check=True,
        **kwargs,
    ):
        super().__init__(alias, platform, api_identifier, options=options, check=check)
        self.log("Container object instanciated")

    @abstractmethod
    def dump_df_to_new_table(self, df, table_name):
        """
        Dumps a dataframe to a new Table having Container for parent

        Args:
            df (DataFrame): Dataframe of data to dump
            table_name: Name to be given to newly created table
        """
        self.log(f"Dumping dataframe to new table named {table_name}")

    def dump_dfs_to_new_tables(self, df_list, table_names):
        """
        Dump a list of dataframes to new Tables having Container for parent

        Args:
            df_list ([DataFrame]): List of dataframes to dump
            table_names ([str]): Names to be given to newly created tables
        """
        self.log("Dumping dataframe list to new tables")
        for df, name in zip(df_list, table_names):
            self.dump_df_to_new_table(df, name)

    @abstractmethod
    def create_table_from_schema(self, table_name, schema, relations=False) -> Table:
        """
        Create an empty table from a schema (list of Tableclone fields)

        Args:
            table_name (str): Name for the new table
            schema (list): List of Fields
            relations (boolean): If true, tableclone will handle relations. If fils, relation fields are treated as text fields.

        Returns:
            Table: Table instance
        """
        self.log(
            f'Creating new table "{table_name}" with schema {[str(field) for field in schema]}'
        )

    def list_children_as_table(self) -> list[Table]:
        """
        returns a list of Table objects

        Returns:
            list: List of Table objects
        """
        return [
            self.CHILD(
                i["name"], self.platform, i["id"], options=self.option_values.values
            )  # type: ignore
            for i in self.platform.list_children(
                self.LIST_LEVEL, parent=self.api_identifier
            )
        ]


class FileContainer(Container):
    MIME_TYPE = ""

    #   Level
    #   Get Schema (list tables, list relations, list types ?)
    #   Table Schema method
    #   Create Table
    #   Create BaseSchema

    # Class Platform
    # Class RestApiPlatform
    # Class PlatformObject
    # Class Table
    # Class FieldListingTable
    # Class PaginatedTable
    # Class GenericTypeMappedTable
    # Class TableSet
