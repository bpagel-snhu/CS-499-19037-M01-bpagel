"""
Bulk Rename Tool

This tool provides functionality for bulk renaming files with various options
including pattern matching, date normalization, and backup creation.
"""

from .rename_logic import perform_batch_rename, build_new_filename, undo_last_batch
from .month_normalize import count_full_months_in_folder, normalize_full_months_in_folder
from .rename_options_frame import RenameOptionsFrame

__version__ = "1.0.0"

__all__ = [
    'perform_batch_rename',
    'build_new_filename', 
    'undo_last_batch',
    'count_full_months_in_folder',
    'normalize_full_months_in_folder',
    'RenameOptionsFrame',
] 