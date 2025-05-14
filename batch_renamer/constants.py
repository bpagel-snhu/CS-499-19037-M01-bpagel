"""
Constants used throughout the batch_renamer package.
"""

# Month mapping for text-to-number conversion
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

# Backup related constants
BACKUP_DIR_NAME = "Renamer Backups"
BACKUP_PREFIX = "Backup_"
BACKUP_EXTENSION = ".zip"

# UI related constants
WINDOW_TITLE = "Bulk File Renamer"
WINDOW_SIZE = "800x450" 