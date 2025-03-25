# batch_renamer/ui/month_normalize.py

import os
import re
import shutil

FULL_MONTH_MAP = {
    "january": "Jan",
    "february": "Feb",
    "march": "Mar",
    "april": "Apr",
    "may": "May",
    "june": "Jun",
    "july": "Jul",
    "august": "Aug",
    "september": "Sep",
    "october": "Oct",
    "november": "Nov",
    "december": "Dec",
}

def count_full_months_in_folder(folder_path: str) -> int:
    """
    Returns how many files in `folder_path` contain spelled-out months
    (January, February, etc.) ignoring case.
    """
    if not os.path.isdir(folder_path):
        return 0

    pattern = re.compile("|".join(FULL_MONTH_MAP.keys()), re.IGNORECASE)
    count = 0
    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        if os.path.isfile(path):
            # check if spelled-out month is found in the filename
            if pattern.search(filename) is not None:
                count += 1
    return count

def normalize_full_months_in_folder(folder_path: str) -> int:
    """
    Renames each file containing spelled-out months to its 3-letter abbreviation.
    Returns the number of files that were renamed.
    """
    if not os.path.isdir(folder_path):
        return 0

    pattern_map = [
        (re.compile(re.escape(full_m), re.IGNORECASE), abbr)
        for full_m, abbr in FULL_MONTH_MAP.items()
    ]
    renamed_count = 0

    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)
        if os.path.isdir(old_path):
            continue

        new_filename = filename
        for pat, abbr in pattern_map:
            if pat.search(new_filename):
                new_filename = pat.sub(abbr, new_filename)

        if new_filename != filename:
            new_path = os.path.join(folder_path, new_filename)
            if not os.path.exists(new_path):
                shutil.move(old_path, new_path)
                renamed_count += 1
            # If there's a collision, you could handle it differently
            else:
                # skip or handle collision
                pass

    return renamed_count
