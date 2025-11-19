import re

import pandas as pd

from ..utils import Option, OptionSet
from .abstracts import (
    Field,
    FieldMapper,
    FieldTypes,
    FileContainer,
    Platform,
    Table,
)


class ExcelFilePlatform(Platform):
    PLATFORM = "excel_file"  # Platform name (for logs, etc.)

    def __init__(
        self, platform_root_path=None, secret_string=None, alias=None, options=None
    ):
        """
        Instantiate a Platform object

        Args:
            platform_root_path(string): Excel file path
            secret_string(string): This is ingnored with excel file
        """
        if not (platform_root_path):
            raise RuntimeError("ExcelFilePlatform requires platform_root_path")
        super().__init__(platform_root_path=platform_root_path)

    def parse_auth_information(self, secret_string):
        """
        Process secret string or other auth information. Checks that enough information is provided
        and that there are no conflicting information
        """
        self.log(
            "parse_auth_information is not used in excel_file  platform", level="debug"
        )

    ##################################
    ############ Requests ############
    ##################################

    def writer(self, engine="openpyxl"):
        """Returns a writer in append mode, ovewriting existing sheets

        Args:
            engine (string):  The engine to use for writing. Options are 'openpyxl' and 'xlsxwriter'.
                              Xlsxwriter offer more options such as strings_to_formula
                              but only supports "w" mode (previous excel file will be overwritten).
        """
        if engine == "openpyxl":
            try:
                return pd.ExcelWriter(
                    self.platform_root_path,
                    engine="openpyxl",
                    mode="a",
                    if_sheet_exists="replace",
                )
            except (FileNotFoundError, Exception):
                # FileNotFoundError: file doesn't exist
                # BadZipFile or other exceptions: file exists but is not a valid Excel file
                # In both cases, create a new Excel file
                return pd.ExcelWriter(
                    self.platform_root_path, engine="openpyxl", mode="w"
                )
        elif engine == "xlsxwriter":
            self.log(
                "Using xlsxwriter engine. Previously existing Excel file will we overwritten"
            )
            return pd.ExcelWriter(
                self.platform_root_path,
                mode="w",
                engine="xlsxwriter",
                engine_kwargs={
                    "options": {"strings_to_urls": False, "strings_to_formulas": False},
                },
            )
        else:
            raise ValueError("Unknown Excel engine")

    ####################################################
    ############ Generic platform interface ############
    ####################################################

    def _list_children_impl(self, level, parent=None):
        """
        Get platform list of "things" depending on the level and the platform
        (base, folder, app, tables, ...)
        """
        with pd.ExcelFile(self.platform_root_path) as xls:
            sheet_names = xls.sheet_names
        return self._make_list_response(
            [{"id": sheet_name, "name": sheet_name} for sheet_name in sheet_names]
        )

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


class ExcelFileTable(Table):
    PLATFORM_CLASS = ExcelFilePlatform

    def __init__(
        self,
        alias,
        platform: ExcelFilePlatform,
        api_identifier,
        options={},
        check=True,
        **kwargs,
    ):
        """
        Excel Table

        Args:
            alias (string): Alias to be used in logs etc.
            platform (Platform | dict): ExcelPlatform instance
            api_identifier (string): Tab name
            check (boolean): If True, will call object_info to check object is valid (e.g. API call is correct)

        Returns:
            Object: ExcelFileTable instance

        """
        super().__init__(alias, platform, api_identifier, options=options)
        if not self.option_values.get(Table.OPT_UNIQUE_ID_COLUMN):
            self.log(
                "No unique id column provided. Most methods requires an unique id column",
                level="warning",
            )

    def get_table_schema(self):
        """
        returns a list of Tableclone Fields
        """
        super().get_table_schema()
        raise NotImplementedError("not yet implemented")

    def get_all(self, modified_after=None):
        raise NotImplementedError("Not needed for ExcelFileTable")

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        self.log("object_info not yet implemented for excel_file")
        return self.make_object_info_response(
            isOk=True, detail="", columns=[], name=self.api_identifier
        )

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        super().parse_api_identifier(api_identifier)
        self.table = self.api_identifier

    def get_all_as_df(self, json_normalize=False, modified_after=None):
        """
        Get all items a Pandas.DataFrame
        """
        df = pd.read_excel(
            self.platform.platform_root_path,
            sheet_name=self.api_identifier,
        )
        if self.unique_id_column:
            df.set_index(self.unique_id_column, drop=True, inplace=True)
        df.index.rename(DATAFRAME_INDEX_NAME, inplace=True)
        return df

    #############################################
    ############ Insert/Update items ############
    #############################################

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
        super().dump_df(df)
        with self.platform.writer() as writer:
            df.to_excel(writer, sheet_name=self.api_identifier)


class ExcelFileContainer(FileContainer):
    OPT_USE_XLSXWRITER_ENGINE = Option(
        "use_xlsxwriter_engine",
        'Default engins is openpyxl. Xlsxwriter offer more options such as strings_to_formulas, but only supports "w" mode (previous excel file will be overwritten)',
        bool,
        False,
    )

    OPTION_SET = OptionSet(
        FileContainer.OPTION_SET.options + [OPT_USE_XLSXWRITER_ENGINE]
    )

    MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PLATFORM_CLASS = ExcelFilePlatform
    CHILD = ExcelFileTable

    def parse_api_identifier(self, api_identifier):
        """
        Process api identifier such as splitting basename, tablename, etc.
        """
        self.log(f"API Identifier is not used on ExcelFile Container", level="warning")

    def _object_info_impl(self):
        """
        Query table to fetch information (such as column list). Can be user to check
        cretential is valid to query the table.
        """
        self.log("object_info not yet implemented for excel_file")
        return self.make_object_info_response(
            isOk=True, detail="", name=self.api_identifier
        )

    def create_table_from_schema(self, table_name, schema, relations=False):
        super().create_table_from_schema(table_name, schema, relations=relations)

    def clean_sheet_name(self, sheet_name):
        """
        Clean sheet name from special characters ('[]:*?/\')
        """
        return re.sub(r"[\[\]\:\*\/\?\\]", "_", sheet_name)

    def dump_df_to_new_table(self, df, table_name):
        """
        Dumps a dataframe to a new Table having Container for parent

        Args:
            df (DataFrame): Dataframe of data to dump
            table_name: Name to be given to newly created table
        """
        # Sheet names should shorter than 31 characters so we truncate them
        super().dump_df_to_new_table(df, table_name)
        if len(table_name) > 31:
            self.log(
                f"Table name {table_name} is longer than 31 characters and will be truncated",
                level="warning",
            )
            sheet_name = self.clean_sheet_name(table_name[:31])
        else:
            sheet_name = self.clean_sheet_name(table_name)
        ExcelFileTable(
            table_name, self.platform, sheet_name, options=self.options
        ).dump_df(df)

    def dump_dfs_to_new_tables(self, df_list, table_names):
        """
        Dump a list of dataframes to new Tables having Container for parent

        Args:
            df_list ([DataFrame]): List of dataframes to dump
            table_names ([str]): Names to be given to newly created tables
        """
        if self.option_values.get(ExcelFileContainer.OPT_USE_XLSXWRITER_ENGINE) == True:
            writer_ = self.platform.writer(engine="xlsxwriter")
        else:
            writer_ = self.platform.writer()

        # We override this function for efficiency (appending tables to an Excel File is slow)
        self.log(f"Dumping dataframe list to new tables")

        # Sheet names should be shorter than 31 characters so we truncate them
        sheet_names = table_names.copy()
        name_counts = {}  # To avoid duplicate names
        for i, name in enumerate(sheet_names):
            if len(name) > 31:
                self.log(
                    f"Table name {name} is longer than 31 characters and will be truncated"
                )
                truncated_name = name[:27] + "..."
                if truncated_name in name_counts:
                    name_counts[truncated_name] += 1
                    truncated_name = (
                        truncated_name[:27] + str(name_counts[truncated_name]) + "..."
                    )
                else:
                    name_counts[truncated_name] = 0
                sheet_names[i] = truncated_name
        # Clean all sheet names with self.clean_sheet_name
        for i, name in enumerate(sheet_names):
            sheet_names[i] = self.clean_sheet_name(name)

        with writer_ as writer:
            for df, name in zip(df_list, sheet_names):
                df.to_excel(writer, sheet_name=name)
