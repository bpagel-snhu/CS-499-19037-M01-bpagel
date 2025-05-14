# batch_renamer/rename_logic.py

from pathlib import Path
from .constants import MONTH_MAPPING
from .utils import get_file_extension, is_valid_directory
from .exceptions import ParseError, ValidationError, FileOperationError
from .logging_config import rename_logger as logger
import os

def parse_filename_position_based(
        filename: str,
        year_start: int,
        year_length: int,
        month_start: int,
        month_length: int,
        day_start: int = None,
        day_length: int = None,
        textual_month: bool = False
) -> tuple[str, str, str]:
    """
    Extract year, month, day from `filename` by character positions.
    If `textual_month` is True, we use only the first 3 letters of the month
    (e.g. "Dec" from "December") and map them to "01"..."12".
    If day_start/day_length is not provided, day might be empty.

    Args:
        filename: The filename to parse
        year_start: Starting position of year
        year_length: Length of year
        month_start: Starting position of month
        month_length: Length of month
        day_start: Optional starting position of day
        day_length: Optional length of day
        textual_month: Whether to parse month as text

    Returns:
        tuple[str, str, str]: (year, month, day) as strings. Day may be empty.

    Raises:
        ParseError: If parsing fails or indices are out of range
    """
    logger.debug(f"Parsing filename: {filename} with positions - "
                f"year({year_start}:{year_start+year_length}), "
                f"month({month_start}:{month_start+month_length}), "
                f"day({day_start}:{day_start+day_length if day_start else 'N/A'})")

    # Calculate how many characters are needed at minimum
    needed_length = max(
        year_start + year_length,
        month_start + month_length,
        (day_start + day_length if day_start is not None and day_length is not None else 0)
    )
    if len(filename) < needed_length:
        error_msg = f"Filename too short for specified positions (needed {needed_length} chars)"
        logger.error(f"{error_msg} - filename: {filename}")
        raise ParseError(error_msg, filename=filename)

    try:
        # Extract raw substrings
        raw_year = filename[year_start:year_start + year_length]
        raw_month = filename[month_start:month_start + month_length]
        raw_day = ""
        if day_start is not None and day_length is not None:
            raw_day = filename[day_start:day_start + day_length]

        logger.debug(f"Raw extracted values - year: {raw_year}, month: {raw_month}, day: {raw_day}")

        # Convert year (assumes user gave correct numeric or text, no transformation needed)
        year = raw_year

        # Convert month
        month = raw_month
        if textual_month:
            # We'll only look at the first 3 letters (lowercased)
            lower_m = month[:3].lower()
            if lower_m in MONTH_MAPPING:
                month = MONTH_MAPPING[lower_m]
                logger.debug(f"Converted textual month '{raw_month}' to '{month}'")
            else:
                error_msg = f"Cannot map textual month '{month}' to a valid numeric month"
                logger.error(error_msg)
                raise ParseError(error_msg, filename=filename)
        else:
            # If numeric month is a single digit, zero-pad
            if month.isdigit() and len(month) == 1:
                month = f"0{month}"

        # Convert day
        day = raw_day
        if day.isdigit() and len(day) == 1:
            day = f"0{day}"

        logger.debug(f"Final parsed values - year: {year}, month: {month}, day: {day}")
        return year, month, day

    except (IndexError, ValueError) as e:
        error_msg = f"Failed to parse filename: {str(e)}"
        logger.error(f"{error_msg} - filename: {filename}")
        raise ParseError(error_msg, filename=filename) from e

def build_new_filename(
        prefix: str,
        year: str,
        month: str,
        day: str,
        separator: str = ""
) -> str:
    """
    Construct a new filename from prefix + date parts (year, month, day).
    If some parts are empty, they're omitted from the final string.
    
    Args:
        prefix: Optional prefix for the filename
        year: Year string
        month: Month string
        day: Day string (can be empty)
        separator: Optional separator between date parts
        
    Returns:
        str: The constructed filename
    """
    logger.debug(f"Building filename with - prefix: {prefix}, year: {year}, "
                f"month: {month}, day: {day}, separator: '{separator}'")
    
    parts = []
    if year:
        parts.append(year)
    if month:
        parts.append(month)
    if day:
        parts.append(day)

    date_str = separator.join(parts) if separator else "".join(parts)
    result = f"{prefix}{date_str}" if prefix else date_str
    
    logger.debug(f"Built filename: {result}")
    return result

def rename_files_in_folder(
        folder_path: str,
        prefix: str = "",
        position_args: dict = None,
        textual_month: bool = False,
        dry_run: bool = True,
        expected_length: int = None
) -> dict:
    """
    Renames files only if their length matches expected_length.
    Tracks skipped files. Prevents renaming of mismatches.
    
    Args:
        folder_path: Path to the folder containing files to rename
        prefix: Optional prefix for renamed files
        position_args: Dictionary containing year/month/day position information
        textual_month: Whether to parse months as text
        dry_run: If True, only simulate the renaming
        expected_length: Required length of filenames to process
        
    Returns:
        dict: Statistics about the operation
        
    Raises:
        ValidationError: If input parameters are invalid
        FileOperationError: If file operations fail
    """
    logger.info(f"Starting rename operation on folder: {folder_path}")
    logger.debug(f"Parameters - prefix: {prefix}, textual_month: {textual_month}, "
                f"dry_run: {dry_run}, expected_length: {expected_length}")

    # Validate inputs
    if not Path(folder_path).is_dir():
        error_msg = f"Invalid folder path: {folder_path}"
        logger.error(error_msg)
        raise ValidationError(error_msg)
        
    if not position_args:
        error_msg = "Position-based parse requires 'position_args' dict"
        logger.error(error_msg)
        raise ValidationError(error_msg)
        
    if expected_length is None:
        error_msg = "Expected filename length must be provided"
        logger.error(error_msg)
        raise ValidationError(error_msg)

    renamed = {}  # Changed from list to dict
    skipped = []
    total_files = 0
    successfully_renamed = 0

    try:
        folder = Path(folder_path)
        filenames = [f for f in folder.iterdir() if f.is_file()]
        total_files = len(filenames)
        logger.info(f"Found {total_files} files to process")

        for file_path in filenames:
            filename = file_path.name
            logger.debug(f"Processing file: {filename}")

            # Check length of filename without extension
            base_name = os.path.splitext(filename)[0]
            if len(base_name) != expected_length:
                logger.debug(f"Skipping {filename} - length mismatch "
                           f"(expected: {expected_length}, got: {len(base_name)})")
                skipped.append(filename)
                continue

            try:
                year, month, day = parse_filename_position_based(
                    base_name,  # Pass base_name instead of filename
                    textual_month=textual_month,
                    **position_args
                )
            except ParseError as e:
                logger.warning(f"Failed to parse {filename}: {e}")
                skipped.append(filename)
                continue

            new_base = build_new_filename(prefix, year, month, day)
            new_name = f"{new_base}{file_path.suffix}"
            new_path = folder / new_name

            # Handle potential filename collisions
            collision_counter = 1
            while not dry_run and new_path.exists():
                logger.debug(f"Filename collision detected for {new_name}")
                new_name = f"{new_base}_{collision_counter}{file_path.suffix}"
                new_path = folder / new_name
                collision_counter += 1

            if not dry_run:
                try:
                    file_path.rename(new_path)
                    renamed[str(file_path)] = str(new_path)  # Add to renamed dict after successful rename
                    successfully_renamed += 1
                    logger.info(f"Renamed {filename} to {new_name}")
                except OSError as e:
                    error_msg = f"Failed to rename {filename}: {e}"
                    logger.error(error_msg)
                    raise FileOperationError(error_msg)
            else:
                renamed[str(file_path)] = str(new_path)  # Add to renamed dict for dry run

        result = {
            "renamed": renamed,
            "skipped": skipped,
            "total": total_files,
            "successful": successfully_renamed,
            "failed": len(skipped)
        }
        logger.info(f"Rename operation completed - {successfully_renamed} renamed, {len(skipped)} skipped")
        return result

    except Exception as e:
        error_msg = f"Unexpected error during rename operation: {e}"
        logger.error(error_msg)
        raise FileOperationError(error_msg)
