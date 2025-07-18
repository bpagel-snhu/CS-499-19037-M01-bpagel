"""
Business logic for folder and file operations in the batch renamer.
"""

from pathlib import Path
from typing import Optional, Tuple
from .exceptions import ValidationError
from .logging_config import ui_logger as logger

class FolderFileManager:
    """Manages folder and file operations and state."""
    
    def __init__(self):
        self._full_folder_path: Optional[str] = None
        self._folder_name: Optional[str] = None
        self._show_full_path: bool = False
        
        self._full_file_path: Optional[str] = None
        self._file_name: Optional[str] = None
        self._show_full_file_path: bool = False
    
    # Folder operations
    def set_folder(self, folder_path: str) -> None:
        """Set the current folder path."""
        if not Path(folder_path).is_dir():
            raise ValidationError(f"Invalid folder path: {folder_path}")
        
        self._full_folder_path = folder_path
        self._folder_name = Path(folder_path).name
        logger.info(f"Folder set to: {folder_path}")
    
    def get_folder_display_path(self) -> str:
        """Get the display path for the current folder."""
        if not self._full_folder_path or not self._folder_name:
            return ""
        return self._full_folder_path if self._show_full_path else self._folder_name
    
    def toggle_folder_path_display(self) -> None:
        """Toggle between full and relative folder path display."""
        self._show_full_path = not self._show_full_path
        logger.debug(f"Folder path display toggled to: {'full' if self._show_full_path else 'relative'}")
    
    # File operations
    def set_file(self, file_path: str) -> None:
        """Set the current file path."""
        if not Path(file_path).is_file():
            raise ValidationError(f"Invalid file path: {file_path}")
        
        self._full_file_path = file_path
        self._file_name = Path(file_path).name
        logger.info(f"File set to: {file_path}")
    
    def get_file_display_path(self) -> str:
        """Get the display path for the current file."""
        if not self._full_file_path or not self._file_name:
            return ""
        return self._full_file_path if self._show_full_file_path else self._file_name
    
    def toggle_file_path_display(self) -> None:
        """Toggle between full and relative file path display."""
        self._show_full_file_path = not self._show_full_file_path
        logger.debug(f"File path display toggled to: {'full' if self._show_full_file_path else 'relative'}")
    
    def clear_file(self) -> None:
        """Clear the current file selection."""
        self._full_file_path = None
        self._file_name = None
        logger.debug("File selection cleared")
    
    def clear_folder(self) -> None:
        """Clear the current folder selection."""
        self._full_folder_path = None
        self._folder_name = None
        logger.debug("Folder selection cleared")
    
    # State accessors
    @property
    def full_folder_path(self) -> Optional[str]:
        return self._full_folder_path
    
    @property
    def folder_name(self) -> Optional[str]:
        return self._folder_name
    
    @property
    def full_file_path(self) -> Optional[str]:
        return self._full_file_path
    
    @property
    def file_name(self) -> Optional[str]:
        return self._file_name
    
    @property
    def show_full_path(self) -> bool:
        return self._show_full_path
    
    @property
    def show_full_file_path(self) -> bool:
        return self._show_full_file_path 