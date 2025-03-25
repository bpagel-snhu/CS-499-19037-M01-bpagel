# batch_renamer/rename_logic.py

import os

# Now we only store the 3-letter forms in our month mapping:
MONTH_MAPPING = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


def parse_filename_position_based(
        filename: str,
        year_start: int,
        year_length: int,
        month_start: int,
        month_length: int,
        day_start: int = None,
        day_length: int = None,
        textual_month: bool = False
) -> (str, str, str):
    """
    Extract year, month, day from `filename` by character positions.
    If `textual_month` is True, we use only the first 3 letters of the month
    (e.g. "Dec" from "December") and map them to "01"..."12".
    If day_start/day_length is not provided, day might be empty.

    Returns (year, month, day) as strings. The day may be '' if not present.
    Raises ValueError on parse error (e.g., if indices are out of range).
    """
    # Calculate how many characters are needed at minimum
    needed_length = max(
        year_start + year_length,
        month_start + month_length,
        (day_start + day_length if day_start is not None and day_length is not None else 0)
    )
    if len(filename) < needed_length:
        raise ValueError(
            f"Filename '{filename}' is too short for the specified positions "
            f"(needed up to index {needed_length - 1})."
        )

    # Extract raw substrings
    raw_year = filename[year_start:year_start + year_length]
    raw_month = filename[month_start:month_start + month_length]

    raw_day = ""
    if day_start is not None and day_length is not None:
        raw_day = filename[day_start: day_start + day_length]

    # Convert year (assumes user gave correct numeric or text, no transformation needed)
    year = raw_year

    # Convert month
    month = raw_month
    if textual_month:
        # We'll only look at the first 3 letters (lowercased)
        # e.g. "December" -> "dec", "Jan" -> "jan"
        lower_m = month[:3].lower()  # use only first 3
        if lower_m in MONTH_MAPPING:
            month = MONTH_MAPPING[lower_m]
        else:
            raise ValueError(f"Cannot map textual month '{month}' to a valid numeric month.")
    else:
        # If numeric month is a single digit, zero-pad
        if month.isdigit() and len(month) == 1:
            month = f"0{month}"

    # Convert day
    day = raw_day
    if day.isdigit() and len(day) == 1:
        day = f"0{day}"

    return year, month, day


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
    Example: if day is empty, result is "YYYYMM".
             if month also empty, result is just "YYYY".
    """
    parts = []
    if year:
        parts.append(year)
    if month:
        parts.append(month)
    if day:
        parts.append(day)

    date_str = separator.join(parts) if separator else "".join(parts)

    if prefix:
        return f"{prefix}{date_str}"
    return date_str


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
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"'{folder_path}' is not a valid folder.")
    if not position_args:
        raise ValueError("Position-based parse requires 'position_args' dict with year/month/day info.")
    if expected_length is None:
        raise ValueError("Expected filename length must be provided.")

    renamed = []
    skipped = []
    total_files = 0
    successfully_renamed = 0

    filenames = os.listdir(folder_path)
    for filename in filenames:
        old_path = os.path.join(folder_path, filename)
        if os.path.isdir(old_path):
            continue  # skip subfolders

        total_files += 1

        # Length check comes FIRST and is absolute
        if len(filename) != expected_length:
            skipped.append(filename)
            continue

        try:
            year, month, day = parse_filename_position_based(
                filename,
                textual_month=textual_month,
                **position_args
            )
        except ValueError:
            skipped.append(filename)
            continue

        ext = os.path.splitext(filename)[1]
        new_base = build_new_filename(prefix, year, month, day)
        new_name = new_base + ext

        # 🔥 Handle potential filename collisions
        new_path = os.path.join(folder_path, new_name)
        collision_counter = 1
        while not dry_run and os.path.exists(new_path):
            new_name = f"{new_base}_{collision_counter}{ext}"
            new_path = os.path.join(folder_path, new_name)
            collision_counter += 1

        renamed.append((filename, new_name))

        if not dry_run:
            os.rename(old_path, new_path)
            successfully_renamed += 1

    return {
        "renamed": renamed,
        "skipped": skipped,
        "total": total_files,
        "successful": successfully_renamed,
        "failed": len(skipped)
    }
