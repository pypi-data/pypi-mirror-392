import fnmatch
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

# Correct import for urlparse and unquote
from urllib.parse import unquote, urlparse

# Assuming pandas is used for DataFrames
import pandas as pd
import requests
from requests.exceptions import RequestException

from ..platforms.bubble import BubblePlatform
from ..platforms.factory import container_factory as cf
from ..utils import Option, OptionSet
from .abstract_task import TaskInterfaceWithWebHookCallbacks


class ContainerFullBackupTask(TaskInterfaceWithWebHookCallbacks):
    """
    Full backup container to container
    """

    OPT_DOWNLOAD_URL_TO_LOCAL_FILE = Option(
        "download_url_to_local_file",
        "Specifies exact table/column pairs containing URLs to attachments. Tableclone downloads the attachment and creates a second column with the local file path.",
        list,
        default_value=[],  # [{"table": ..., "columns" : [...]},...]
    )
    OPT_DOWNLOAD_URLS_FROM_GLOB = Option(
        "download_urls_from_glob",
        "Provide a list of glob patterns (e.g., 'https://*.s3.amazonaws.com/*'). Tableclone scans all string cells, extracts URLs matching any pattern, and downloads them to a structured local directory (destination_base_path/table_name/column_name/). Does not modify the DataFrame.",
        list,  # List of strings (glob patterns)
        default_value=[],
    )
    OPT_TABLE_FILTER = Option(
        "table_filter",
        "List of table names to backup. If empty or not provided, all tables will be backed up",
        list,
        default_value=[],  # ["table1", "table2", ...]
    )
    OPTION_SET = OptionSet(
        [OPT_DOWNLOAD_URL_TO_LOCAL_FILE, OPT_DOWNLOAD_URLS_FROM_GLOB, OPT_TABLE_FILTER]
    )

    URL_REGEX = re.compile(r"(?:https?:)?//[^\s()<>]+?(?=[,\s)]|$)")

    def _validate_config(self, config: dict) -> dict:
        return super()._validate_config(config)

    def _setup(self):
        self._source = cf(
            self.config["source"]["platform"], **self.config["source"]["container"]
        )
        self._destination = cf(
            self.config["destination"]["platform"],
            **self.config["destination"]["container"],
        )

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    def _preprocess_url(self, url: str) -> str:
        """
        Preprocess URL for platform-specific requirements
        """
        if isinstance(self.source.platform, BubblePlatform) and url.startswith("//"):
            self.log(f"Prepending 'https:' to Bubble URL: {url}", "debug")
            return "https:" + url
        return url

    def _extract_filename_from_headers(self, headers) -> Optional[str]:
        """
        Extract filename from Content-Disposition header
        """
        content_disposition = headers.get("Content-Disposition")
        if content_disposition:
            disp_parts = content_disposition.split("filename=")
            if len(disp_parts) > 1:
                filename = unquote(disp_parts[1].strip('" '))
                self.log(f"Filename from Content-Disposition: {filename}", "debug")
                return filename
        return None

    def _extract_filename_from_url(self, url: str) -> Optional[str]:
        """
        Extract filename from URL path as fallback
        """
        try:
            parsed_url = urlparse(url)
            path_part = Path(unquote(parsed_url.path))
            if path_part.name:
                self.log(f"Filename from URL path: {path_part.name}", "debug")
                return path_part.name
        except Exception as e:
            self.log(f"Could not extract filename from URL path {url}: {e}", "warning")
        return None

    def _get_fallback_filename(self, url: str) -> str:
        """
        Get fallback filename when other methods fail
        """
        potential_name = Path(url).name
        filename = potential_name if potential_name else "downloaded_file"
        self.log(f"Using fallback filename: {filename}", "warning")
        return filename

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing invalid characters and truncating if needed
        """
        invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
        safe_filename = re.sub(invalid_chars, "_", filename)

        max_len = 240
        if len(safe_filename) > max_len:
            name_part, ext_part = Path(safe_filename).stem, Path(safe_filename).suffix
            safe_filename = name_part[: max_len - len(ext_part)] + ext_part
            self.log(f"Truncated filename to: {safe_filename}", "debug")

        return safe_filename

    def _save_response_to_file(self, response, file_path: Path):
        """
        Save HTTP response content to file
        """
        self.log(f"Saving file to {file_path}", "info")
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def download_url_to_local_file(
        self, url: str, local_directory: str = "attachments"
    ) -> str:
        """
        Downloads a file from a URL and saves it to a local file
        """
        url = self._preprocess_url(url)
        self.log(f"Attempting download from URL: {url}", "debug")

        target_dir = Path(local_directory)
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            with requests.Session() as session:
                with session.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()

                    # Try multiple methods to get filename
                    attachment_name = (
                        self._extract_filename_from_headers(r.headers)
                        or self._extract_filename_from_url(url)
                        or self._get_fallback_filename(url)
                    )

                    safe_attachment_name = self._sanitize_filename(attachment_name)
                    local_file_path = target_dir / safe_attachment_name

                    self._save_response_to_file(r, local_file_path)

            return str(local_file_path)

        except RequestException as e:
            self.log(f"Download failed for {url}: {type(e).__name__} - {e}", "error")
            raise
        except Exception as e:
            self.log(
                f"An unexpected error occurred during download of {url}: {type(e).__name__} - {e}",
                "error",
            )
            raise

    def _download_attachments_from_url_config(
        self,
        df: pd.DataFrame,
        table_alias: str,
        table_dl_configs: list[dict],
        download_root_dir: Path,
    ):
        """
        Processes downloads based on the OPT_DOWNLOAD_URL_TO_LOCAL_FILE config.
        Downloads URLs from specified columns and replaces cell content with directory path.
        Modifies the DataFrame in place.
        """
        if not table_dl_configs:
            return  # Rien à faire pour cette table

        self.log(
            f"Processing specific URL downloads for table '{table_alias}' based on config."
        )
        for dl_config in table_dl_configs:
            target_columns = dl_config.get("columns", [])
            if not target_columns:
                continue

            self.log(f"Target columns for table '{table_alias}': {target_columns}")
            for url_column in target_columns:
                if url_column not in df.columns:
                    self.log(
                        f"Column '{url_column}' not found in table '{table_alias}', skipping.",
                        "warning",
                    )
                    continue

                for index, row in df.iterrows():
                    url = row[url_column]
                    # Utilise pd.isna() pour gérer les NaN, None, etc. en plus de vérifier le type
                    if isinstance(url, str) and url and not pd.isna(url):
                        local_save_dir = (
                            download_root_dir
                            / str(table_alias)
                            / url_column
                            / str(index)
                        )
                        try:
                            _ = self.download_url_to_local_file(
                                url,
                                str(local_save_dir),
                            )
                            # Replace cell content with relative directory path
                            relative_path = local_save_dir.relative_to(
                                download_root_dir
                            )
                            df.at[index, url_column] = str(relative_path)
                            self.log(
                                f"Replaced cell content with relative directory path '{relative_path}' for index {index}",
                                "debug",
                            )
                        except Exception as e:
                            self.log(
                                f"Error processing specific URL '{url}' in column '{url_column}', table '{table_alias}': {e}",
                                "warning",
                            )
                            df.at[index, url_column] = "ERROR_DOWNLOADING"

    def _extract_urls_from_cell(self, cell_value) -> list[str]:
        """Extract URLs from a cell value using regex."""
        if not isinstance(cell_value, str) or not cell_value:
            return []
        return self.URL_REGEX.findall(cell_value)

    def _find_matching_pattern(
        self, url: str, glob_patterns: list[str]
    ) -> Optional[str]:
        """Find the first glob pattern that matches the URL, or None if no match."""
        for pattern in glob_patterns:
            if fnmatch.fnmatch(url, pattern):
                return pattern
        return None

    def _download_url_for_cell(
        self,
        url: str,
        pattern: str,
        table_alias: str,
        col_name: str,
        index,
        file_counter: int,
        download_root_dir: Path,
    ) -> str:
        """
        Download a single URL for a specific cell.
        Returns the local file path on success.
        Raises exception on failure.
        """
        self.log(
            f"URL '{url}' matched glob pattern '{pattern}' in table '{table_alias}', column '{col_name}', row {index}. Attempting download.",
            "info",
        )

        # Create directory structure: table/column/row/file_number
        local_save_dir = (
            download_root_dir
            / str(table_alias)
            / col_name
            / str(index)
            / str(file_counter)
        )

        local_file_path = self.download_url_to_local_file(url, str(local_save_dir))

        self.log(
            f"Downloaded file for cell [{index}, '{col_name}'] to '{local_file_path}'",
            "debug",
        )

        return local_file_path

    def _download_single_url_task(
        self,
        url: str,
        pattern: str,
        table_alias: str,
        col_name: str,
        index,
        file_counter: int,
        download_root_dir: Path,
    ) -> tuple[int, str, str]:
        """
        Download a single URL and return the result.
        Returns (file_counter, result_type, result_value) where:
        - result_type is 'success' or 'error'
        - result_value is the file path on success or error message on failure
        """
        try:
            local_file_path = self._download_url_for_cell(
                url,
                pattern,
                table_alias,
                col_name,
                index,
                file_counter,
                download_root_dir,
            )
            return (file_counter, "success", local_file_path)
        except Exception as e:
            error_msg = f"Error downloading glob-matched URL '{url}' found in table '{table_alias}', column '{col_name}', row {index}: {e}"
            self.log(error_msg, "warning")
            return (file_counter, "error", "ERROR_DOWNLOADING")

    def _process_single_column(
        self,
        df: pd.DataFrame,
        col_name: str,
        glob_patterns: list[str],
        table_alias: str,
        download_root_dir: Path,
    ):
        """Process all cells in a single column for URL downloads with parallel cell processing."""
        self.log(f"Processing column '{col_name}' in table '{table_alias}'", "debug")

        # Collect cells with URLs to process
        cells_to_process = []
        for index, row in df.iterrows():
            cell_value = row[col_name]
            urls = self._extract_urls_from_cell(cell_value)
            if urls:
                cells_to_process.append((index, urls))

        if not cells_to_process:
            return

        # Process cells in parallel
        max_workers = min(len(cells_to_process), 5)  # Limit concurrent cell processing
        self.log(
            f"Processing {len(cells_to_process)} cells with {max_workers} workers",
            "debug",
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit cell processing tasks
            future_to_cell = {
                executor.submit(
                    self._process_cell_urls,
                    df,
                    urls,
                    glob_patterns,
                    table_alias,
                    col_name,
                    index,
                    download_root_dir,
                ): (index, urls)
                for index, urls in cells_to_process
            }

            # Wait for all cells to complete
            for future in as_completed(future_to_cell):
                index, urls = future_to_cell[future]
                try:
                    future.result()
                    self.log(
                        f"Completed processing cell [{index}, '{col_name}']", "debug"
                    )
                except Exception as e:
                    self.log(
                        f"Error processing cell [{index}, '{col_name}'] in table '{table_alias}': {e}",
                        "error",
                    )

    def _process_cell_urls(
        self,
        df: pd.DataFrame,
        urls: list[str],
        glob_patterns: list[str],
        table_alias: str,
        col_name: str,
        index,
        download_root_dir: Path,
    ):
        """Process all URLs found in a single cell sequentially."""
        processed_urls = set()  # Track processed URLs to avoid duplicates
        file_counter = 1
        download_success = False

        # Create the directory path for this cell's downloads
        cell_download_dir = download_root_dir / str(table_alias) / col_name / str(index)

        # Process URLs sequentially
        for url in urls:
            if not isinstance(url, str) or url in processed_urls:
                continue

            matching_pattern = self._find_matching_pattern(url, glob_patterns)
            if matching_pattern:
                processed_urls.add(url)
                try:
                    _ = self._download_url_for_cell(
                        url,
                        matching_pattern,
                        table_alias,
                        col_name,
                        index,
                        file_counter,
                        download_root_dir,
                    )
                    download_success = True
                    file_counter += 1
                except Exception as e:
                    error_msg = f"Error downloading glob-matched URL '{url}' found in table '{table_alias}', column '{col_name}', row {index}: {e}"
                    self.log(error_msg, "warning")

        # Replace cell content with relative directory path if any download succeeded
        if download_success:
            relative_path = cell_download_dir.relative_to(download_root_dir)
            df.at[index, col_name] = str(relative_path)
            self.log(
                f"Replaced cell content with relative directory path '{relative_path}' for table '{table_alias}', column '{col_name}', row {index}",
                "debug",
            )
        else:
            df.at[index, col_name] = "ERROR_DOWNLOADING"

    def _download_attachments_from_globs(
        self,
        df: pd.DataFrame,
        table_alias: str,
        glob_patterns: list[str],
        download_root_dir: Path,
    ):
        """
        Processes downloads based on the OPT_DOWNLOAD_URLS_FROM_GLOB config.
        Scans all string cells, finds URLs matching glob patterns, and downloads them.
        Replaces original cell content with directory path containing downloaded files.
        Processes columns sequentially, but parallelizes cell processing within each column.
        """
        if not glob_patterns:
            return

        self.log(
            f"Scanning table '{table_alias}' for URLs matching glob patterns: {glob_patterns}"
        )

        # Get all columns to process
        columns_to_process = list(df.columns)

        if not columns_to_process:
            return

        self.log(
            f"Processing {len(columns_to_process)} columns sequentially",
            "info",
        )

        # Process columns sequentially
        for col_name in columns_to_process:
            try:
                self._process_single_column(
                    df,
                    col_name,
                    glob_patterns,
                    table_alias,
                    download_root_dir,
                )
                self.log(f"Completed processing column '{col_name}'", "debug")
            except Exception as e:
                self.log(
                    f"Error processing column '{col_name}' in table '{table_alias}': {e}",
                    "error",
                )

    def _process_impl(self):
        tables = self.source.list_children_as_table()

        # Récupérer les options une seule fois
        download_url_configs = self.options_values.get(
            ContainerFullBackupTask.OPT_DOWNLOAD_URL_TO_LOCAL_FILE,
        )
        glob_patterns = self.options_values.get(
            ContainerFullBackupTask.OPT_DOWNLOAD_URLS_FROM_GLOB,
        )

        # Déterminer le répertoire racine pour tous les téléchargements
        destination_platform_path = Path(self.destination.platform.platform_root_path)
        download_root_dir = (
            destination_platform_path.parent
            # if destination_platform_path.is_file()
            # else destination_platform_path
        )
        self.log(f"Base directory for downloads: {download_root_dir}", "info")

        processed_dfs = []
        table_names = []

        table_filter = self.options_values.get(ContainerFullBackupTask.OPT_TABLE_FILTER)
        if table_filter:
            tables = [table for table in tables if table.alias in table_filter]
            self.log(
                f"Filtering tables to: {[table.alias for table in tables]}", "info"
            )
        else:
            self.log(
                f"Backing up all tables: {[table.alias for table in tables]}", "info"
            )

        for table in tables:
            table_alias = str(table.alias)  # Assurer que c'est une string
            self.log(f"Processing table: {table_alias}")
            try:
                df = table.get_all_as_df()
            except Exception as e:
                self.log(
                    f"Failed to get DataFrame for table '{table_alias}': {e}", "error"
                )
                continue  # Passer à la table suivante

            if download_url_configs:
                # Filtrer les configurations pour la table actuelle
                table_specific_configs = [
                    dl_config
                    for dl_config in download_url_configs
                    if dl_config.get("table")
                    == table_alias  # Comparaison directe avec l'alias
                ]
                if table_specific_configs:
                    self._download_attachments_from_url_config(
                        df, table_alias, table_specific_configs, download_root_dir
                    )

            if glob_patterns:
                self._download_attachments_from_globs(
                    df, table_alias, glob_patterns, download_root_dir
                )

            processed_dfs.append(df)
            table_names.append(table_alias)
            self.log(f"Finished processing table: {table_alias}")

        if processed_dfs:
            self.log(f"Dumping {len(processed_dfs)} processed tables to destination...")
            try:
                self.destination.dump_dfs_to_new_tables(processed_dfs, table_names)
                self.log("Finished dumping tables.")
            except Exception as e:
                self.log(f"Error dumping tables to destination: {e}", "critical")
                raise e
        else:
            self.log("No tables were processed or retrieved.", "warning")

        return {}  # Garder la signature de retour originale
