import argparse
import json
import logging
import os
from pathlib import Path
from string import Template

# from .v1_parser import process_json
from .tasking.full_backup import ContainerFullBackupTask
from .tasking.table_sync_task import TableSyncTask


def init_logging(level=logging.INFO):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[console_handler],
    )


def substitute_env_vars(config):
    """Recursively substitute environment variables in configuration"""
    if isinstance(config, dict):
        return {key: substitute_env_vars(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [substitute_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Utiliser string.Template pour substituer les variables
        return Template(config).safe_substitute(os.environ)
    else:
        return config


def load_config(config_arg):
    """Load configuration from a string or a file path"""
    try:
        # Attempt to parse config_arg as a JSON string first
        config = json.loads(config_arg)
    except json.JSONDecodeError:
        # If config_arg is not a JSON string, assume it's a file path
        path = Path(config_arg)
        if path.is_file():
            config = json.loads(path.read_text())
        else:
            raise ValueError(
                f"'{config_arg}' is neither valid JSON nor a valid file path."
            )

    # Process environment variables in config
    return substitute_env_vars(config)


def full_backup(args):
    config = load_config(args.config)
    if not isinstance(config, dict):
        raise TypeError("Configuration must be a dictionary")
    ContainerFullBackupTask(config).process()


def sync(args):
    config = load_config(args.config)
    if not isinstance(config, dict):
        raise TypeError("Configuration must be a dictionary")
    TableSyncTask(config).process()


def main():
    parser = argparse.ArgumentParser(description="Table cloning operations")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Full backup subcommand
    full_backup_parser = subparsers.add_parser(
        "full_backup", help="Perform a full backup"
    )
    full_backup_parser.add_argument(
        "config", help="JSON configuration string or path to JSON file"
    )

    # Sync subcommand
    sync_parser = subparsers.add_parser("sync", help="Perform a table sync")
    sync_parser.add_argument(
        "config", help="JSON configuration string or path to JSON file"
    )

    args = parser.parse_args()
    init_logging()

    if args.command == "full_backup":
        full_backup(args)
    elif args.command == "sync":
        sync(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
