"""
Utility functions used throughout the batch_renamer package.
"""

import os
from pathlib import Path
from typing import Optional
from .constants import CONFIG_DIR_NAME, BACKUP_DIR_NAME, CONFIG_FILE_NAME, FONT_FAMILY, FONT_SIZE_NORMAL
import customtkinter as ctk
import json


def get_backup_directory() -> Path:
    """
    Get the path to the backup directory in the user's home directory (hidden .bpfu/backups folder).
    Returns:
        Path: Path object pointing to the backup directory
    """
    backup_dir = Path.home() / CONFIG_DIR_NAME / BACKUP_DIR_NAME
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


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
    config_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / CONFIG_FILE_NAME
    if not config_file.exists():
        default_config = {"backup_destination": str(backup_dir)}
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


def create_button(parent, text: str, command, width: Optional[int] = None,
                  fg_color: Optional[str] = None, hover_color: Optional[str] = None,
                  text_color: Optional[str] = None) -> ctk.CTkButton:
    """
    Create a standardized button with common properties.
    
    Args:
        parent: Parent widget
        text: Button text
        command: Command to execute on click
        width: Optional button width
        fg_color: Optional foreground color
        hover_color: Optional hover color
        text_color: Optional text color
        
    Returns:
        ctk.CTkButton: The created button
    """
    kwargs = {
        "master": parent,
        "text": text,
        "command": command,
        "font": (FONT_FAMILY, FONT_SIZE_NORMAL)
    }

    # Only add optional parameters if they are not None
    if width is not None:
        kwargs["width"] = width
    if fg_color is not None:
        kwargs["fg_color"] = fg_color
    if hover_color is not None:
        kwargs["hover_color"] = hover_color
    if text_color is not None:
        kwargs["text_color"] = text_color

    return ctk.CTkButton(**kwargs)


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
