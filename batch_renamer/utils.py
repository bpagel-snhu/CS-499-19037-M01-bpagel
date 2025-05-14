"""
Utility functions used throughout the batch_renamer package.
"""

import os
from pathlib import Path
from typing import Optional

def get_backup_directory() -> Path:
    """
    Get the path to the backup directory in the user's Downloads folder.
    
    Returns:
        Path: Path object pointing to the backup directory
    """
    downloads_dir = Path.home() / "Downloads"
    backup_dir = downloads_dir / "Renamer Backups"
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