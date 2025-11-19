from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from ..platforms.abstracts import InsertUpdateUpsertTable, Table
from ..platforms.factory import table_factory as tf
from ..utils import Option, OptionSet
from .abstract_task import TaskInterfaceWithWebHookCallbacks


class TableSyncTask(TaskInterfaceWithWebHookCallbacks):
    """
    Full backup container to container

    Example config :
        {
            "task_id": "",
            "source": {
                "platform": "airtable",
                "table": {
                    "alias": "xxxx",
                    "api_identifier": "xxxx",
                    "options": {},
                    "platform": {
                        "secret_string": "xxx",
                        "platform_root_path": "yyy",
                        "options": {
                            "allowed_columns": ["col1", "col2"],
                            ...
                        }
                    }
                }
            },
            "destination": {
                "platform": "sqlite",
                "table": {
                    "alias": "xxxx",
                    "api_identifier": "xxxx",
                    "options": {},
                    "platform": {
                        "platform_root_path": "yyy",
                        "options": {}
                    }
                }
            },

            "options": {
                mapping: {
                    "columns": {
                        "src_col_name": "dst_col_name",
                        ...
                    },
                },
                "primary_key_dst": "",
                "primary_key_src": ""
            }
            "success_callback": [
                {
                    "url": "xxx",
                    "params": {},
                    "headers": {}"
                }
            ]
            "error_callback": [
                {
                    "url": "xxx",
                    "params": {},
                    "headers": {}"
                }
            ]
        }
    """

    OPT_MAPPING = Option(
        "mapping",
        "Mapping of columns",
        dict,
    )
    OPT_MAPPING_AUTO = Option(
        "mapping_auto",
        "Use automapping (column names must match)",
        bool,
        default_value=False,
    )
    OPT_DST_COMMON_UNIQUE_ID_COLUMN = Option(
        "dst_common_unique_id_column",
        "Common unique ID between source and destination tables, upon which sync will be based",
        str,
        required=True,
    )
    OPT_SRC_COMMON_UNIQUE_ID_COLUMN = Option(
        "src_common_unique_id_column",
        "Common unique ID between source and destination tables, upon which sync will be based",
        str,
    )
    OPT_SRC_USE_NATIVE_ID_AS_COMMON_UNIQUE_ID = Option(
        "src_use_native_id_as_common_unique_id",
        "Use native ID for source table",
        bool,
        incompatible_with=[OPT_SRC_COMMON_UNIQUE_ID_COLUMN],
    )
    OPT_SYNC_APPEND_MODE = Option(
        "append_mode",
        "Append new rows from source to destination based on unique ID comparison",
        bool,
        default_value=False,
    )
    OPT_SYNC_UPDATE_MODE = Option(
        "update_mode",
        "Update existing rows from destination based on unique ID comparison",
        bool,
        default_value=False,
    )
    OPT_SYNC_DELETE_MODE = Option(
        "delete_mode",
        "Delete rows in destination if not present in source",
        bool,
        default_value=False,
    )
    OPT_LAST_MODIFICATION_TIMEWINDOW = Option(
        "timewindow",
        "Only consider records based on last modification date",
        str,
        enum=["1 month", "1 week", "1 day"],
    )
    OPT_EXPORT_CSV = Option(
        "export_csv",
        "Export CSV files for debugging",
        bool,
        default_value=False,
    )
    OPTION_SET = OptionSet(
        [
            OPT_MAPPING,
            OPT_MAPPING_AUTO,
            OPT_DST_COMMON_UNIQUE_ID_COLUMN,
            OPT_SRC_COMMON_UNIQUE_ID_COLUMN,
            OPT_SRC_USE_NATIVE_ID_AS_COMMON_UNIQUE_ID,
            OPT_SYNC_APPEND_MODE,
            OPT_SYNC_UPDATE_MODE,
            OPT_SYNC_DELETE_MODE,
            OPT_LAST_MODIFICATION_TIMEWINDOW,
            OPT_EXPORT_CSV,
        ]
    )

    def _validate_config(self, config: dict) -> dict:
        super()._validate_config(config)
        # Task options should  contain OPT_SRC_COMMON_UNIQUE_ID_COLUMN or OPT_SRC_USE_NATIVE_ID_AS_COMMON_UNIQUE_ID
        if not self.options_values.get(
            TableSyncTask.OPT_SRC_COMMON_UNIQUE_ID_COLUMN
        ) and not self.options_values.get(TableSyncTask.OPT_SRC_USE_NATIVE_ID_AS_COMMON_UNIQUE_ID):
            raise ValueError(
                f"Task option {TableSyncTask.OPT_SRC_COMMON_UNIQUE_ID_COLUMN.name} or {TableSyncTask.OPT_SRC_USE_NATIVE_ID_AS_COMMON_UNIQUE_ID.name} is required"
            )

        return config

    def _setup(self):
        self._source = tf(
            self.config["source"]["platform"],
            **self.config["source"]["table"],
        )
        self._destination = tf(
            self.config["destination"]["platform"],
            **self.config["destination"]["table"],
        )

        # Timewindow
        if self.options_values.get(TableSyncTask.OPT_LAST_MODIFICATION_TIMEWINDOW):
            value = self.options_values.get(TableSyncTask.OPT_LAST_MODIFICATION_TIMEWINDOW)
            if value == "1 month":
                self.modified_after_ = (datetime.now() - relativedelta(months=1)).isoformat()
            elif value == "1 week":
                self.modified_after_ = (datetime.now() - relativedelta(weeks=1)).isoformat()
            elif value == "1 day":
                self.modified_after_ = (datetime.now() - relativedelta(days=1)).isoformat()

            self.log(
                f"Detecting option timewindow: records modified after {self.modified_after_} will be consideder"
            )

        else:
            self.modified_after_ = None

    @property
    def source(self) -> Table:
        return self._source

    @property
    def destination(self) -> Table:
        return self._destination

    def _process_impl(self):
        if self.options_values.get(TableSyncTask.OPT_MAPPING):
            columns_mapping = self.options_values.get(TableSyncTask.OPT_MAPPING)
        else:
            # Auto map
            columns_mapping = self.source.auto_map(self.destination)

        self.log(f"Syncing table {self.source} to {self.destination}")
        if (
            isinstance(self.destination, InsertUpdateUpsertTable)
            and self.destination.UPSERT
            and self.options_values.get(TableSyncTask.OPT_SYNC_APPEND_MODE)
            and self.options_values.get(TableSyncTask.OPT_SYNC_UPDATE_MODE)
        ):
            return self.upsert_sync(columns_mapping)

        else:
            return self.simple_sync(columns_mapping)

    def get_src_reshaped_df(self, columns_mapping) -> pd.DataFrame:
        """
        Returns a dataframe
        - with the columns mapping applied
        - with modified_after filter applied
        """
        # Getting source DF
        src_df = self.source.get_sanitized_df(
            date_normalize=True, modified_after=self.modified_after_
        )
        export_csv = self.options_values.get(TableSyncTask.OPT_EXPORT_CSV)

        if export_csv:
            src_df.to_csv("_debug/csv_src.csv")

        # If a src_common_unique_id_column if provided, we test unicity
        # and reindex DF according to this column
        # If not, we use the native index, unicity have already been checked

        if self.options_values.get(TableSyncTask.OPT_SRC_COMMON_UNIQUE_ID_COLUMN):
            src_unique_id = self.options_values.get(TableSyncTask.OPT_SRC_COMMON_UNIQUE_ID_COLUMN)
            self.log(f"Using source common unique id column {src_unique_id}")
            if (
                src_df.index.name != src_unique_id
            ):  # in case table have been loadet with OPT_UNIQUE_ID_COLUMN
                if not src_df[src_unique_id].is_unique:
                    raise IndexError("Provided source common unique id is not unique")
        else:
            # _validate_config() should have already checked that OPT_SRC_COMMON_UNIQUE_ID_COLUMN,
            # then OPT_SRC_USE_NATIVE_ID_AS_COMMON_UNIQUE_ID have been set
            src_unique_id = self.source.table_index_name()
            self.log("No source common unique id provided. Using native index")

        dst_unique_id = self.options_values.get(TableSyncTask.OPT_DST_COMMON_UNIQUE_ID_COLUMN)

        # We complete mapping with dst_unique_id -> src_unique_id
        mapping_ = columns_mapping.copy()
        mapping_[src_unique_id] = dst_unique_id

        # Reshaping DF to make them comparable
        # if source has an  OPT_UNIQUE_ID_COLUMN (i.e; index is not native ID), we drop it because it is aready present

        src_df_reshaped = (
            src_df.reset_index(drop=False)  # index (src_unique_id or native id) is added to columns
            .loc[:, mapping_.keys()]
            .rename(columns=mapping_)
        )  # type: ignore

        if export_csv:
            src_df_reshaped.to_csv("_debug/csv_src_reshaped.csv")

        return src_df_reshaped

    def upsert_sync(self, columns_mapping: dict):
        if isinstance(self.destination, InsertUpdateUpsertTable) and self.destination.UPSERT:
            dst_unique_id = self.options_values.get(TableSyncTask.OPT_DST_COMMON_UNIQUE_ID_COLUMN)
            src_df_reshaped = self.get_src_reshaped_df(columns_mapping)

            self.log(f"{len(src_df_reshaped)}  records to upsert in destination")
            if len(src_df_reshaped) > 0:
                self.destination.upsert(src_df_reshaped, dst_unique_id)
                upserted_row_count = len(src_df_reshaped)
            else:
                upserted_row_count = 0
            # callback
            return {
                "src_row_count": upserted_row_count,
                "inserted_row_count": upserted_row_count,
                "updated_row_count": upserted_row_count,
            }
        else:
            raise RuntimeError("upsert_sync only implemented for upsert tables")

    def simple_sync(self, columns_mapping: dict):
        if isinstance(self.destination, InsertUpdateUpsertTable):
            # Getting destination DF, exluding empty primary_key
            dst_df = self.destination.get_sanitized_df(
                date_normalize=True, modified_after=self.modified_after_
            )

            # Sanitizing based on dst_unique_id
            dst_unique_id = self.options_values.get(TableSyncTask.OPT_DST_COMMON_UNIQUE_ID_COLUMN)

            # Handle empty destination table or missing unique_id column
            if len(dst_df) == 0 or dst_unique_id not in dst_df.columns:
                self.log("Destination table is empty, all source records will be inserted")
                src_df_reshaped = self.get_src_reshaped_df(columns_mapping)

                inserted_row_count = 0
                if self.options_values.get(TableSyncTask.OPT_SYNC_APPEND_MODE):
                    self.log(f"{len(src_df_reshaped)} new records to insert in destination")
                    if len(src_df_reshaped) > 0:
                        self.destination.insert(src_df_reshaped)
                        inserted_row_count = len(src_df_reshaped)
                else:
                    self.log(
                        f"Option {TableSyncTask.OPT_SYNC_APPEND_MODE} not provided. Skipping new records creation"
                    )

                return {
                    "src_row_count": len(src_df_reshaped),
                    "inserted_row_count": inserted_row_count,
                    "updated_row_count": 0,
                }

            dst_df = dst_df.dropna(subset=[dst_unique_id])
            dst_df = dst_df.loc[dst_df[dst_unique_id] != "", :]

            export_csv = self.options_values.get(TableSyncTask.OPT_EXPORT_CSV)
            if export_csv:
                dst_df.to_csv("_debug/csv_dst.csv")

            if not dst_df[dst_unique_id].is_unique:
                raise IndexError(
                    f"Values of column {dst_unique_id} in table {self.destination} are not unique"
                )
            self.log(
                f"{len(dst_df)} records in destination have usable unique ID (empty values ignored)"
            )

            src_df_reshaped = self.get_src_reshaped_df(columns_mapping)

            # SOURCE AND DEST COMPARISON (hybrid approach: merge for IDs, then index-based filtering)

            # Step 1: Merge ONLY on unique IDs to identify insert/update/delete operations
            # This avoids dealing with column suffixes (_src/_dst) and is very clear
            merged_ids = src_df_reshaped[[dst_unique_id]].merge(
                dst_df[[dst_unique_id]],
                on=dst_unique_id,
                how='outer',
                indicator=True
            )

            # Step 2: Extract IDs for each operation
            insert_ids = merged_ids[merged_ids['_merge'] == 'left_only'][dst_unique_id]
            potential_update_ids = merged_ids[merged_ids['_merge'] == 'both'][dst_unique_id]
            delete_ids = merged_ids[merged_ids['_merge'] == 'right_only'][dst_unique_id]

            self.log(
                f"{len(insert_ids)} new records, {len(potential_update_ids)} existing records, "
                f"{len(delete_ids)} records only in destination"
            )

            # Step 3: For records in both, use index-based filtering + compare()
            # This preserves the natural pandas workflow and keeps destination index intact
            value_cols = list(columns_mapping.values())

            if len(potential_update_ids) > 0:
                # Filter and index both DataFrames on dst_unique_id
                src_for_compare = src_df_reshaped.set_index(dst_unique_id, drop=True).loc[potential_update_ids, value_cols]
                dst_for_compare = dst_df.set_index(dst_unique_id, drop=True).loc[potential_update_ids, value_cols]

                if export_csv:
                    src_for_compare.to_csv("_debug/csv_src_for_compare.csv")
                    dst_for_compare.to_csv("_debug/csv_dst_for_compare.csv")

                # Use pandas compare() to detect actual changes (handles NaN properly)
                comparison = dst_for_compare.compare(src_for_compare)
                updated_values_ids = comparison.index if len(comparison) > 0 else pd.Index([])

                if export_csv and len(comparison) > 0:
                    comparison.to_csv("_debug/csv_compare.csv")
            else:
                updated_values_ids = pd.Index([])

            self.log(f"Compared source and destination, {len(updated_values_ids)} records to update")

            # Step 4: Execute operations based on options
            inserted_row_count = 0
            updated_row_count = 0
            deleted_row_count = 0

            # INSERT: New records from source
            if self.options_values.get(TableSyncTask.OPT_SYNC_APPEND_MODE):
                if len(insert_ids) > 0:
                    # Filter source records to insert and set index with dst_unique_id
                    # (respects tableclone convention: DataFrame indexed with platform Unique ID)
                    new_records = src_df_reshaped[src_df_reshaped[dst_unique_id].isin(insert_ids)]
                    new_records = new_records.set_index(dst_unique_id, drop=False)
                    self.log(f"{len(new_records)} new records to insert in destination")
                    self.destination.insert(new_records)
                    inserted_row_count = len(new_records)
                else:
                    self.log("No new records to insert")
            else:
                self.log(
                    f"Option {TableSyncTask.OPT_SYNC_APPEND_MODE} not provided. Skipping new records creation"
                )

            # UPDATE: Modified records
            if self.options_values.get(TableSyncTask.OPT_SYNC_UPDATE_MODE):
                if len(updated_values_ids) > 0:
                    # Filter destination records by updated IDs to preserve destination index
                    # Then merge with source values
                    updated_records = dst_df.loc[
                        dst_df[dst_unique_id].isin(updated_values_ids), [dst_unique_id]
                    ].merge(
                        src_df_reshaped.set_index(dst_unique_id, drop=True),
                        how="inner",
                        left_on=dst_unique_id,
                        right_index=True,
                    )
                    self.log(f"{len(updated_records)} records to update in destination")
                    self.destination.update(updated_records)
                    updated_row_count = len(updated_records)
                else:
                    self.log("No records to update")
            else:
                self.log(
                    f"Option {TableSyncTask.OPT_SYNC_UPDATE_MODE} not provided. Skipping existing records update"
                )

            # DELETE: Records only in destination (not yet supported but structure is ready)
            if self.options_values.get(TableSyncTask.OPT_SYNC_DELETE_MODE):
                if len(delete_ids) > 0:
                    self.log(f"{len(delete_ids)} records to delete from destination")
                    # When platform supports delete:
                    # self.destination.delete(delete_ids.tolist())
                    # deleted_row_count = len(delete_ids)
                    self.log("Delete operation not yet implemented for this platform")
                else:
                    self.log("No records to delete")
            else:
                if len(delete_ids) > 0:
                    self.log(
                        f"Option {TableSyncTask.OPT_SYNC_DELETE_MODE} not provided. "
                        f"{len(delete_ids)} records only in destination will be ignored"
                    )

            # callback
            src_row_count = len(src_df_reshaped)
            return {
                "src_row_count": src_row_count,
                "inserted_row_count": inserted_row_count,
                "updated_row_count": updated_row_count,
            }
        else:
            raise RuntimeError("Not implemented for this table")
