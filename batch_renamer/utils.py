"""
Utility functions used throughout the batch_renamer package.
"""

import os
from pathlib import Path
from typing import Optional
import json
import sys
import subprocess
from .constants import (
    CONFIG_DIR_NAME, BACKUP_DIR_NAME, LOGS_DIR_NAME, DATABASE_DIR_NAME, CONFIG_FILE_NAME
)


def get_backup_directory() -> Path:
    """
    Get the path to the backup directory in the user's home directory (hidden .bpfu/backups folder).
    Returns:
        Path: Path object pointing to the backup directory
    """
    backup_dir = Path.home() / CONFIG_DIR_NAME / BACKUP_DIR_NAME
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_logs_directory() -> Path:
    """
    Get the path to the logs directory in the user's home directory (hidden .bpfu/logs folder).
    Returns:
        Path: Path object pointing to the logs directory
    """
    logs_dir = Path.home() / CONFIG_DIR_NAME / LOGS_DIR_NAME
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_config_file_path() -> Path:
    """
    Get the path to the config file in the hidden .bpfu directory in the user's home directory.
    Returns:
        Path: Path object pointing to the config file
    """
    config_dir = Path.home() / CONFIG_DIR_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILE_NAME


def initialize_user_config() -> None:
    """
    Ensure the .bpfu folder and config file exist in the user's home directory. If the config file does not exist, create it with default settings.
    """
    config_dir = Path.home() / CONFIG_DIR_NAME
    backup_dir = config_dir / BACKUP_DIR_NAME
    logs_dir = config_dir / LOGS_DIR_NAME
    database_dir = config_dir / DATABASE_DIR_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    database_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / CONFIG_FILE_NAME
    if not config_file.exists():
        default_config = {
            "backup_destination": str(backup_dir),
            "logs_destination": str(logs_dir),
            "database_destination": str(database_dir)
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory to check/create
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        filename: Name of the file
        
    Returns:
        str: File extension (including the dot)
    """
    return os.path.splitext(filename)[1]


def is_valid_directory(path: str) -> bool:
    """
    Check if a path is a valid directory.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if path is a valid directory, False otherwise
    """
    if path is None:
        return False
    return os.path.isdir(path)


def get_display_path(full_path: str, name: str, show_full: bool) -> str:
    """
    Get the appropriate display path based on the show_full flag.
    
    Args:
        full_path: Full path to the file/folder
        name: Name of the file/folder
        show_full: Whether to show the full path
        
    Returns:
        str: The path to display
    """
    return full_path if show_full else name


def copy_to_clipboard(text: str, parent_window) -> None:
    """
    Copy text to clipboard and show a toast notification.
    
    Args:
        text: Text to copy
        parent_window: Parent window for showing toast
    """
    parent_window.clipboard_clear()
    parent_window.clipboard_append(text)
    parent_window.show_toast("Copied to clipboard!")


def get_backup_destination_from_config() -> Path:
    """
    Read the backup destination from the config file. If not set or config is missing, return the default backup directory.
    Returns:
        Path: Path to the backup destination
    """
    config_file = get_config_file_path()
    default_backup_dir = Path.home() / CONFIG_DIR_NAME / BACKUP_DIR_NAME
    if not config_file.exists():
        return default_backup_dir
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        backup_dest = config.get("backup_destination")
        if backup_dest:
            return Path(backup_dest)
        else:
            return default_backup_dir
    except Exception:
        return default_backup_dir


def set_backup_destination_in_config(new_path: str) -> None:
    """
    Update the backup destination in the config file.
    Args:
        new_path: The new backup destination path as a string
    """
    config_file = get_config_file_path()
    config = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    config["backup_destination"] = new_path
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_logs_destination_from_config() -> Path:
    """
    Read the logs destination from the config file. If not set or config is missing, return the default logs directory.
    Returns:
        Path: Path to the logs destination
    """
    config_file = get_config_file_path()
    default_logs_dir = Path.home() / CONFIG_DIR_NAME / LOGS_DIR_NAME
    if not config_file.exists():
        return default_logs_dir
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        logs_dest = config.get("logs_destination")
        if logs_dest:
            return Path(logs_dest)
        else:
            return default_logs_dir
    except Exception:
        return default_logs_dir


def set_logs_destination_in_config(new_path: str) -> None:
    """
    Update the logs destination in the config file.
    Args:
        new_path: The new logs destination path as a string
    """
    config_file = get_config_file_path()
    config = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    config["logs_destination"] = new_path
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_database_destination_from_config() -> Path:
    """
    Read the database destination from the config file. If not set or config is missing, return the default database directory.
    Returns:
        Path: Path to the database destination
    """
    config_file = get_config_file_path()
    default_db_dir = Path.home() / CONFIG_DIR_NAME / DATABASE_DIR_NAME
    if not config_file.exists():
        return default_db_dir
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        db_dest = config.get("database_destination")
        if db_dest:
            return Path(db_dest)
        else:
            return default_db_dir
    except Exception:
        return default_db_dir


def set_database_destination_in_config(new_path: str) -> None:
    """
    Update the database destination in the config file.
    Args:
        new_path: The new database destination path as a string
    """
    config_file = get_config_file_path()
    config = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    config["database_destination"] = new_path
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def move_database_file(old_path: Path, new_path: Path) -> bool:
    """
    Move the database file from old_path to new_path.
    
    Args:
        old_path: Current database file path
        new_path: New database file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the new directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move the database file
        import shutil
        shutil.move(str(old_path), str(new_path))
        return True
    except Exception as e:
        print(f"Failed to move database file: {e}")
        return False


def open_in_file_explorer(path):
    """Open the given path in the system's file explorer, cross-platform."""
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
