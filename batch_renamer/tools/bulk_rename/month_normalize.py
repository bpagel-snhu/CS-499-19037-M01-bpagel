# batch_renamer/tools/bulk_rename/month_normalize.py

import os
import re
import shutil
from ...logging_config import ui_logger as logger
from ...exceptions import FileOperationError, ValidationError
from ...constants import MONTH_MAPPING

FULL_MONTH_MAP = {month: data["abbr"] for month, data in MONTH_MAPPING.items()}

def count_full_months_in_folder(folder_path: str) -> int:
    """
    Returns how many files in `folder_path` contain spelled-out months
    (January, February, etc.) ignoring case, excluding May.
    
    Args:
        folder_path: Path to the folder to check
        
    Returns:
        Number of files containing full month names (excluding May)
        
    Raises:
        ValidationError: If folder_path is not a valid directory
    """
    logger.debug(f"Counting full month names in folder: {folder_path}")
    if not os.path.isdir(folder_path):
        logger.error(f"Invalid folder path: {folder_path}")
        raise ValidationError(f"Invalid folder path: {folder_path}")

    # Use the same list of full months as our test setup, excluding May
    full_months = [
        "January", "February", "March", "April", "June", "July", 
        "August", "September", "October", "November", "December"
    ]
    pattern = re.compile("|".join(full_months), re.IGNORECASE)
    count = 0
    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        if os.path.isfile(path):
            # check if spelled-out month is found in the filename
            if pattern.search(filename) is not None:
                count += 1
                logger.debug(f"Found full month name in file: {filename}")
    
    logger.info(f"Found {count} files with full month names (excluding May)")
    return count

def normalize_full_months_in_folder(folder_path: str) -> int:
    """
    Renames each file containing spelled-out months to its 3-letter abbreviation.
    Handles filename collisions by appending a sequential marker (_1, _2, etc.).
    Only counts successful renames in the returned count.
    
    Args:
        folder_path: Path to the folder containing files to normalize
        
    Returns:
        Number of files that were successfully renamed
        
    Raises:
        ValidationError: If folder_path is not a valid directory
        FileOperationError: If file operations fail
    """
    logger.info(f"Normalizing full month names in folder: {folder_path}")
    if not os.path.isdir(folder_path):
        logger.error(f"Invalid folder path: {folder_path}")
        raise ValidationError(f"Invalid folder path: {folder_path}")

    pattern_map = [
        (re.compile(re.escape(full_m), re.IGNORECASE), abbr)
        for full_m, abbr in FULL_MONTH_MAP.items()
    ]
    renamed_count = 0
    skipped_count = 0

    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)
        if os.path.isdir(old_path):
            logger.debug(f"Skipping directory: {filename}")
            continue

        new_filename = filename
        for pat, abbr in pattern_map:
            if pat.search(new_filename):
                new_filename = pat.sub(abbr, new_filename)
                logger.debug(f"Replacing month name in: {filename} -> {new_filename}")

        if new_filename != filename:
            new_path = os.path.join(folder_path, new_filename)
            # Handle collisions by appending _1, _2, etc.
            if os.path.exists(new_path):
                base, ext = os.path.splitext(new_filename)
                counter = 1
                while True:
                    candidate = f"{base}_{counter}{ext}"
                    candidate_path = os.path.join(folder_path, candidate)
                    if not os.path.exists(candidate_path):
                        new_path = candidate_path
                        new_filename = candidate
                        break
                    counter += 1
                try:
                    shutil.move(old_path, new_path)
                    renamed_count += 1
                    logger.info(f"Renamed: {filename} -> {new_filename}")
                except Exception as e:
                    logger.error(f"Failed to rename {filename}: {str(e)}", exc_info=True)
                    raise FileOperationError(f"Failed to rename {filename}: {str(e)}")

    logger.info(f"Month normalization complete: {renamed_count} renamed, {skipped_count} skipped")
    return renamed_count
