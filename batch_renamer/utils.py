"""
Utility functions used throughout the batch_renamer package.
"""

import os
from pathlib import Path
from typing import Optional
from .constants import BACKUP_DIR_NAME, FONT_FAMILY, FONT_SIZE_NORMAL
import customtkinter as ctk


def get_backup_directory() -> Path:
    """
    Get the path to the backup directory in the user's Downloads folder.
    
    Returns:
        Path: Path object pointing to the backup directory
    """
    downloads_dir = Path.home() / "Downloads"
    backup_dir = downloads_dir / BACKUP_DIR_NAME
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


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
