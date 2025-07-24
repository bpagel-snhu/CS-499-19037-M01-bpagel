"""
Batch Renamer - A tool for bulk renaming files based on position-based date extraction.
"""

from .tools.bulk_rename.rename_logic import (
    parse_filename_position_based,
    build_new_filename,
    rename_files_in_folder
)
from .backup_logic import (
    create_backup_interactive,
    create_folder_backup
)
from .ui.main_window import BatchRename

__version__ = "1.0.0"

__all__ = [
    # Core functionality
    'parse_filename_position_based',
    'build_new_filename',
    'rename_files_in_folder',
    
    # Backup functionality
    'create_backup_interactive',
    'create_folder_backup',
    
    # UI
    'BatchRename',
    
    # Version
    '__version__',
]
