from .abstracts import Container, Platform, Table
from .airtable import AirtableBase, AirtablePlatform, AirtableTable
from .bubble import BubbleBase, BubblePlatform, BubbleTable
from .excel_file import ExcelFileContainer, ExcelFilePlatform, ExcelFileTable
from .gdrive import GdriveFolderContainer, GdrivePlatform
from .ksaar import KsaarPlatform, KsaarTable
from .postgresql import PostgrePlatform, PostgreTable
from .sqlite import SqliteDB, SqlitePlatform, SqliteTable
from .timetonic import TimetonicPlatform, TimetonicTable

PLATFORMS = {
    AirtablePlatform.PLATFORM: AirtablePlatform,
    BubblePlatform.PLATFORM: BubblePlatform,
    PostgrePlatform.PLATFORM: PostgrePlatform,
    KsaarPlatform.PLATFORM: KsaarPlatform,
    TimetonicPlatform.PLATFORM: TimetonicPlatform,
    GdrivePlatform.PLATFORM: GdrivePlatform,
    SqlitePlatform.PLATFORM: SqlitePlatform,
    ExcelFilePlatform.PLATFORM: ExcelFilePlatform,
}

TABLES = {
    AirtablePlatform.PLATFORM: AirtableTable,
    BubblePlatform.PLATFORM: BubbleTable,
    PostgrePlatform.PLATFORM: PostgreTable,
    KsaarPlatform.PLATFORM: KsaarTable,
    TimetonicPlatform.PLATFORM: TimetonicTable,
    GdrivePlatform.PLATFORM: GdriveFolderContainer,
    SqlitePlatform.PLATFORM: SqliteTable,
    ExcelFilePlatform.PLATFORM: ExcelFileTable,
}

CONTAINERS = {
    GdrivePlatform.PLATFORM: GdriveFolderContainer,
    AirtablePlatform.PLATFORM: AirtableBase,
    SqlitePlatform.PLATFORM: SqliteDB,
    ExcelFilePlatform.PLATFORM: ExcelFileContainer,
    BubblePlatform.PLATFORM: BubbleBase,
}


def container_factory(
    platform_name,
    alias,
    platform: Platform | dict,
    api_identifier=None,
    options=None,
    check=True,
    **kwargs,
) -> Container:
    container_class = CONTAINERS.get(platform_name.lower())
    if container_class is None:
        raise ValueError(f"Unsupported platform: {platform_name}")

    return container_class(
        alias,
        platform,
        api_identifier,
        options=options,
        check=check,
        **kwargs,
    )


def table_factory(
    # TO DO  : doc and fix redundancy
    platform_name,
    alias,
    platform: Platform | dict,
    api_identifier,
    options=None,
    check=True,
    **kwargs,
) -> Table:
    """Returns a Table instance

    Args:
        platform_name (string): String identifier of the platform
        alias (string): Alias to be used in logs etc.
        platform (Platform | dict): Either a Platform instance or a dict of kwargs to create a Platform instance
        api_identifier (string): ID of the object. Can be None, for sqlite DB container for example
        options(dict): specific options
        check(boolean): if True, will call object_info() upon instance creation
    """
    table_class = TABLES.get(platform_name.lower())
    if table_class is None:
        raise ValueError(f"Unsupported platform: {platform_name}")

    return table_class(
        alias,
        platform,
        api_identifier,
        options=options,
        check=check,
        **kwargs,
    )


def platform_factory(
    platform_name, platform_root_path=None, secret_string=None, alias=None, options=None
):
    platform_class = PLATFORMS.get(platform_name.lower())
    if platform_class is None:
        raise ValueError(f"Unsupported platform: {platform_name}")

    return platform_class(
        platform_root_path=platform_root_path,
        secret_string=secret_string,
        alias=alias,
        options=options,
    )
