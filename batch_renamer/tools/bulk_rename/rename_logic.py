# batch_renamer/tools/bulk_rename/rename_logic.py

from pathlib import Path
from ...constants import MONTH_MAPPING
from ...utils import get_file_extension, is_valid_directory
from ...exceptions import ParseError, ValidationError, FileOperationError
from ...logging_config import rename_logger as logger
import os

from .undo_commands import RenameCommand, BatchOperation

# Global undo stack for the session
undo_stack: list[BatchOperation] = []

def perform_batch_rename(folder, prefix, position_args, textual_month, dry_run, expected_length, progress_callback=None):
    """
    Performs a batch rename operation with undo support.
    Runs a dry-run first to get the mapping, then executes and records the batch if not dry_run.
    Returns the result dict from rename_files_in_folder.
    Now pushes the batch to undo_stack before execution for partial undo support.
    """
    # Always do a dry run first to get the mapping
    if progress_callback:
        progress_callback(0.0, "Analyzing files...")
        
    dry_run_result = rename_files_in_folder_with_progress(
        folder, prefix, position_args,
        textual_month=textual_month,
        dry_run=True,
        expected_length=expected_length,
        progress_callback=progress_callback
    ) if progress_callback else rename_files_in_folder(
        folder, prefix, position_args,
        textual_month=textual_month,
        dry_run=True,
        expected_length=expected_length
    )

    renamed_map = dry_run_result["renamed"]  # dict of old_path → new_path

    batch = BatchOperation()
    for old, new in renamed_map.items():
        batch.add(RenameCommand(old, new))

    if not dry_run:
        undo_stack.append(batch)  # Push before execution
        try:
            if progress_callback:
                progress_callback(0.8, "Executing rename operations...")
            batch.execute_all()
        except Exception as e:
            logger.error(f"Batch rename failed: {e}")
            raise FileOperationError(f"Batch rename failed: {e}")
        # Return a result based on the dry run, but with correct stats
        result = dry_run_result.copy()
        result["successful"] = len(renamed_map)
        result["skipped"] = []
        result["failed"] = 0
        return result
    else:
        return dry_run_result

def undo_last_batch(folder_path=None, confirm_partial=False, dry_run=False):
    """
    Robust undo for the last batch rename operation.
    Returns a result dict with status and details.
    If partial undo is needed, only proceeds if confirm_partial is True.
    If dry_run is True, only preview what would happen (no file changes).
    """
    if not undo_stack:
        return {"status": "empty"}
    batch = undo_stack[-1]
    # Pass dry_run directly
    result = batch.undo(folder_path=folder_path, dry_run=dry_run)
    if not dry_run:
        if result["status"] == "success" or result["status"] == "already_restored":
            undo_stack.pop()
        elif result["status"] == "partial":
            if confirm_partial:
                undo_stack.pop()
            # else: keep batch for possible retry
        # If conflict or empty, do not pop
    return result


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
                 f"year({year_start}:{year_start + year_length}), "
                 f"month({month_start}:{month_start + month_length}), "
                 f"day({day_start}:{day_start + day_length if day_start else 'N/A'})")

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
            # Check if this matches any month's abbreviation
            for month_data in MONTH_MAPPING.values():
                if month_data["abbr"].lower() == lower_m:
                    month = month_data["num"]
                    logger.debug(f"Converted textual month '{raw_month}' to '{month}'")
                    break
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
    Now collision-safe in dry-run and real run.
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

    renamed = {}  # old_path -> new_path
    skipped = []
    total_files = 0
    successfully_renamed = 0
    seen_targets = {}  # base_name -> count

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
            # Collision-safe candidate name
            cnt = seen_targets.get(new_base, 0)
            candidate = new_base
            while True:
                candidate_name = f"{candidate}{file_path.suffix}" if cnt == 0 else f"{candidate}_{cnt}{file_path.suffix}"
                new_path = folder / candidate_name
                # Check both disk and in-memory mapping
                if not new_path.exists() and (str(new_path) not in renamed.values()):
                    break
                cnt += 1
            seen_targets[new_base] = cnt
            renamed[str(file_path)] = str(new_path)

        # Real run: perform renames
        if not dry_run:
            for old, new in renamed.items():
                try:
                    Path(old).rename(new)
                    successfully_renamed += 1
                    logger.info(f"Renamed {os.path.basename(old)} to {os.path.basename(new)}")
                except OSError as e:
                    error_msg = f"Failed to rename {old} to {new}: {e}"
                    logger.error(error_msg)
                    skipped.append(os.path.basename(old))

        result = {
            "renamed": renamed,
            "skipped": skipped,
            "total": total_files,
            "successful": successfully_renamed if not dry_run else len(renamed),
            "failed": len(skipped)
        }
        logger.info(f"Rename operation completed - {result['successful']} renamed, {len(skipped)} skipped")
        return result

    except Exception as e:
        error_msg = f"Unexpected error during rename operation: {e}"
        logger.error(error_msg)
        raise FileOperationError(error_msg)


def rename_files_in_folder_with_progress(
        folder_path: str,
        prefix: str = "",
        position_args: dict = None,
        textual_month: bool = False,
        dry_run: bool = True,
        expected_length: int = None,
        progress_callback=None
) -> dict:
    """
    Renames files with progress updates.
    Renames files only if their length matches expected_length.
    Tracks skipped files. Prevents renaming of mismatches.
    Now collision-safe in dry-run and real run.
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

    renamed = {}  # old_path -> new_path
    skipped = []
    total_files = 0
    successfully_renamed = 0
    seen_targets = {}  # base_name -> count

    try:
        folder = Path(folder_path)
        filenames = [f for f in folder.iterdir() if f.is_file()]
        total_files = len(filenames)
        logger.info(f"Found {total_files} files to process")

        if total_files == 0:
            if progress_callback:
                progress_callback(1.0, "No files found to process")
            return {
                "renamed": {},
                "skipped": [],
                "total": 0,
                "successful": 0,
                "failed": 0
            }

        for i, file_path in enumerate(filenames):
            filename = file_path.name
            
            # Update progress
            if progress_callback:
                progress_value = (i + 1) / total_files
                if not progress_callback(progress_value, f"Processing: {filename}"):
                    logger.info("Rename operation cancelled by user")
                    return {
                        "renamed": renamed,
                        "skipped": skipped,
                        "total": total_files,
                        "successful": successfully_renamed if not dry_run else len(renamed),
                        "failed": len(skipped)
                    }
            
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
            # Collision-safe candidate name
            cnt = seen_targets.get(new_base, 0)
            candidate = new_base
            while True:
                candidate_name = f"{candidate}{file_path.suffix}" if cnt == 0 else f"{candidate}_{cnt}{file_path.suffix}"
                new_path = folder / candidate_name
                # Check both disk and in-memory mapping
                if not new_path.exists() and (str(new_path) not in renamed.values()):
                    break
                cnt += 1
            seen_targets[new_base] = cnt
            renamed[str(file_path)] = str(new_path)

        # Real run: perform renames
        if not dry_run:
            for j, (old, new) in enumerate(renamed.items()):
                # Update progress for rename phase
                if progress_callback:
                    progress_value = (total_files + j + 1) / (total_files + len(renamed))
                    if not progress_callback(progress_value, f"Renaming: {os.path.basename(old)}"):
                        logger.info("Rename operation cancelled by user")
                        break
                        
                try:
                    Path(old).rename(new)
                    successfully_renamed += 1
                    logger.info(f"Renamed {os.path.basename(old)} to {os.path.basename(new)}")
                except OSError as e:
                    error_msg = f"Failed to rename {old} to {new}: {e}"
                    logger.error(error_msg)
                    skipped.append(os.path.basename(old))

        result = {
            "renamed": renamed,
            "skipped": skipped,
            "total": total_files,
            "successful": successfully_renamed if not dry_run else len(renamed),
            "failed": len(skipped)
        }
        
        # Final progress update
        if progress_callback:
            progress_callback(1.0, f"Complete! Renamed {result['successful']} of {total_files} files")
            
        logger.info(f"Rename operation completed: {result['successful']} successful, {result['failed']} failed")
        return result

    except Exception as e:
        logger.error(f"Rename operation failed: {e}")
        raise FileOperationError(f"Rename operation failed: {e}")
