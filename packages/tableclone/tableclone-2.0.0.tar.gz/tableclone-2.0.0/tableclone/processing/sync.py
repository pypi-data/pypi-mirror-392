import logging
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from ..platforms import Platform, Table

LOGGER = logging.getLogger(__name__)

# Value used in client tu use native unique ID
OPTION_PLATFORM_NATIVE_ID = "platform native ID"

OPTION_NAME_SYNC_MODE = "sync_mode"
OPTION_VALUE_SYNC_MODE_APPEND = "append"
OPTION_VALUE_SYNC_MODE_UPDATE = "update"
OPTION_VALUE_SYNC_MODE_APPEND_UPDATE = "append&update"


def simple_sync(
    src_table: Table,
    dst_table: Table,
    mapping,
    dst_unique_id,
    src_unique_id=None,
    options=None,
    export_csv=False,
):
    """
    Sync src table to dst table.

    All line not present in dst (based on primary key) will be added.
    All lines present in dst (based on primary key) will be updated according to src

    Args:
        src_table (Table): Source table
        dst_table (Table): Destination table
        mapping (dict): Mapping between src columns and dst  columns
        dst_unique_id (Union[str,int]): Columns in destination containing unique id used to compare tables
        src_unique_id (Union[str,int]): Columns in source containing the primary key. If not,
                                        native primary id will be used (record_id, bubble_id...)
        options(dict):  Options
        callback(function): Callback function to call after sync.
                            Signature callback(src_row_count, inserted_row_count, updated_row_count)
    """
    LOGGER.info(f"Syncing table {src_table} to {dst_table}")
    LOGGER.info(f"Options: {options}")
    if options.get("timewindow"):
        if options.get("timewindow") == "1 month":
            modified_after_ = (datetime.now() - relativedelta(months=1)).isoformat()
        elif options.get("timewindow") == "1 week":
            modified_after_ = (datetime.now() - relativedelta(weeks=1)).isoformat()
        elif options.get("timewindow") == "1 day":
            modified_after_ = (datetime.now() - relativedelta(days=1)).isoformat()
        elif options.get("timewindow") == "all":
            modified_after_ = None
        LOGGER.info(
            f"Detecting option timewindow: records modified after {modified_after_} will be consideder"
        )
    else:
        modified_after_ = None

    # Getting destination DF, exluding empty primary_key
    dst_df = dst_table.get_sanitized_df(
        date_normalize=True, modified_after=modified_after_
    )

    # Sanitizing based on dst_unique_id
    dst_df = dst_df.dropna(subset=[dst_unique_id])
    dst_df = dst_df[dst_df[dst_unique_id] != ""]

    if not dst_df[dst_unique_id].is_unique:
        raise IndexError(
            f"Values of column {dst_unique_id} in table {dst_table} are not unique"
        )
    LOGGER.info(
        f"{len(dst_df)} records in destination have usable unique ID (empty values ignored)"
    )

    # Getting source DF
    src_df = src_table.get_sanitized_df(
        date_normalize=True, modified_after=modified_after_
    )

    # If a source primary key (unique identifier) if provided, we test unicity
    # and reindex DF according to this column
    if (
        src_unique_id
        and src_unique_id != ""
        and src_unique_id != OPTION_PLATFORM_NATIVE_ID
    ):
        LOGGER.info(f"Using source unique id {src_unique_id}")
        if not src_df[src_unique_id].is_unique:
            raise IndexError("Provided source primary key is not unique")
        src_df = src_df.set_index(src_unique_id)
        src_df.index.rename(Platform.DATAFRAME_INDEX_NAME, inplace=True)
    else:
        LOGGER.info("No source primary key provided. Using native index")

    src_ids = src_df.index

    # SOURCE AND DEST COMPARISON
    # List of unique ID in destination that still exists in source.
    existing_ids = dst_df[dst_unique_id][dst_df[dst_unique_id].isin(src_ids)]
    LOGGER.info(f"{len(existing_ids)} records from source alredy exists in destination")

    # We sort DF to compare source and destination
    dst_df = dst_df.sort_values(by=[dst_unique_id])
    src_df = src_df.sort_index()

    if export_csv:
        src_df.to_csv("_debug/csv_src.csv")
        dst_df.to_csv("_debug/csv_dst.csv")

    # Reshaping DF to make them comparable
    src_df_reshaped = src_df.loc[existing_ids, :]
    src_df_reshaped = src_df_reshaped[mapping.keys()].rename(columns=mapping)

    dst_df_reshaped = dst_df.set_index(dst_unique_id, drop=False)
    dst_df_reshaped = dst_df_reshaped.loc[existing_ids, mapping.values()]

    if export_csv:
        src_df_reshaped.to_csv("_debug/csv_src_reshaped.csv")
        dst_df_reshaped.to_csv("_debug/csv_dst_reshaped.csv")

    # Extract only the ids to update
    updated_values_ids = dst_df_reshaped.compare(src_df_reshaped).index
    LOGGER.info(
        "Compared source and destination, %s records to update"
        % (len(updated_values_ids))
    )

    if export_csv:
        dst_df_reshaped.compare(
            src_df_reshaped, result_names=("destination", "source")
        ).to_csv("_debug/csv_compare.csv")

    sync_mode = options.get(OPTION_NAME_SYNC_MODE)
    # Preparing callback
    inserted_row_count = 0
    updated_row_count = 0

    if (
        sync_mode != OPTION_VALUE_SYNC_MODE_UPDATE
    ):  # works if option is none or append&update for historic compat
        # Creating new records
        new_records = src_df.loc[~src_df.index.isin(existing_ids), list(mapping.keys())]
        new_records = (
            new_records.rename(columns=mapping)
            .reset_index()
            .rename(columns={Platform.DATAFRAME_INDEX_NAME: dst_unique_id})
        )
        LOGGER.info("%s new records to insert in destination" % len(new_records))
        if len(new_records) > 0:
            dst_table.insert(new_records)
            inserted_row_count = len(new_records)
    else:
        LOGGER.info(f"{sync_mode} mode. Skipping new records creation")

    if (
        sync_mode != OPTION_VALUE_SYNC_MODE_APPEND
    ):  # works if option is none or append&update for historic compat
        # updating existing records
        # TODO: use reshaped df
        updated_records = (
            dst_df.loc[dst_df[dst_unique_id].isin(updated_values_ids), :]
            .reset_index()[[Platform.DATAFRAME_INDEX_NAME, dst_unique_id]]
            .merge(
                src_df[mapping.keys()],
                how="inner",
                left_on=dst_unique_id,
                right_index=True,
            )
            .set_index(Platform.DATAFRAME_INDEX_NAME)
        )
        updated_records = updated_records.rename(columns=mapping)[
            list(mapping.values()) + [dst_unique_id]
        ]
        LOGGER.info("%s records to update in destination" % len(updated_records))
        if len(updated_records) > 0:
            dst_table.update(updated_records)
            updated_row_count = len(updated_records)
    else:
        LOGGER.info(f"{sync_mode} mode. Skipping existing records update")

    # callback
    src_row_count = len(src_df)
    return src_row_count, inserted_row_count, updated_row_count


def upsert_sync(
    src_table: Table,
    dst_table: Table,
    mapping,
    dst_unique_id,
    src_unique_id=None,
    options=None,
    export_csv=False,
):
    LOGGER.info(f"Syncing (UPSERT) table {src_table} to {dst_table}")
    LOGGER.info(f"Options: {options}")
    if options.get("timewindow"):
        if options.get("timewindow") == "1 month":
            modified_after_ = (datetime.now() - relativedelta(months=1)).isoformat()
        elif options.get("timewindow") == "1 week":
            modified_after_ = (datetime.now() - relativedelta(weeks=1)).isoformat()
        elif options.get("timewindow") == "1 day":
            modified_after_ = (datetime.now() - relativedelta(days=1)).isoformat()
        elif options.get("timewindow") == "all":
            modified_after_ = None
        LOGGER.info(
            f"Detecting option timewindow: records modified after {modified_after_} will be consideder"
        )
    else:
        modified_after_ = None

    # Getting source DF
    src_df = src_table.get_sanitized_df(
        date_normalize=True, modified_after=modified_after_
    )

    # If a source primary key (unique identifier) if provided, we test unicity
    # and reindex DF according to this column
    if (
        src_unique_id
        and src_unique_id != ""
        and src_unique_id != OPTION_PLATFORM_NATIVE_ID
    ):
        LOGGER.info(f"Using source unique id {src_unique_id}")
        if not src_df[src_unique_id].is_unique:
            raise IndexError("Provided source primary key is not unique")
        src_df = src_df.set_index(src_unique_id)
        src_df.index.rename(Platform.DATAFRAME_INDEX_NAME, inplace=True)
    else:
        LOGGER.info("No source primary key provided. Using native index")

    src_ids = src_df.index

    if export_csv:
        src_df.to_csv("_debug/csv_src.csv")

    # Reshaping DF to make them comparable
    src_df_reshaped = src_df[mapping.keys()].rename(columns=mapping)

    if export_csv:
        src_df_reshaped.to_csv("_debut/csv_src_reshaped.csv")

    new_records = src_df_reshaped.reset_index().rename(
        columns={Platform.DATAFRAME_INDEX_NAME: dst_unique_id}
    )
    LOGGER.info("%s new records to insert in destination" % len(new_records))
    if len(new_records) > 0:
        dst_table.upsert(new_records, dst_unique_id)
        inserted_row_count = len(new_records)
    else:
        inserted_row_count = 0
    # callback
    src_row_count = len(src_df)
    return src_row_count, inserted_row_count, inserted_row_count
