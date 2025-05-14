"""
Constants used throughout the batch_renamer package.
"""

# Month mapping for text-to-number conversion
MONTH_MAPPING = {
    "january": {"abbr": "Jan", "num": "01"},
    "february": {"abbr": "Feb", "num": "02"},
    "march": {"abbr": "Mar", "num": "03"},
    "april": {"abbr": "Apr", "num": "04"},
    "may": {"abbr": "May", "num": "05"},
    "june": {"abbr": "Jun", "num": "06"},
    "july": {"abbr": "Jul", "num": "07"},
    "august": {"abbr": "Aug", "num": "08"},
    "september": {"abbr": "Sep", "num": "09"},
    "october": {"abbr": "Oct", "num": "10"},
    "november": {"abbr": "Nov", "num": "11"},
    "december": {"abbr": "Dec", "num": "12"},
}

# Backup related constants
BACKUP_DIR_NAME = "Renamer Backups"
BACKUP_PREFIX = "Backup_"
BACKUP_EXTENSION = ".zip"

# UI related constants
WINDOW_TITLE = "Bulk File Renamer"
WINDOW_SIZE = "800x450" 