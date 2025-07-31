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
CONFIG_DIR_NAME = ".bpfu"  # Hidden folder in home directory for config and backups
BACKUP_DIR_NAME = "backups"  # Subfolder inside .bpfu for backups
LOGS_DIR_NAME = "logs"  # Subfolder inside .bpfu for logs
DATABASE_DIR_NAME = "database"  # Subfolder inside .bpfu for database files
LOG_RETENTION_COUNT = 10  # Number of most recent log files to keep
CONFIG_FILE_NAME = "config.json"
BACKUP_PREFIX = "Backup_"
BACKUP_EXTENSION = ".zip"

# UI related constants
WINDOW_TITLE = "Barron Pagel | File Utilities"
WINDOW_SIZE = "800x400"
WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 400

# UI Component Sizes
SLIDER_WIDTH = 250
PREFIX_ENTRY_WIDTH = 200
PREVIEW_ENTRY_WIDTH = 300

# UI Padding and Spacing
FRAME_PADDING = 20
GRID_PADDING = 5
GRID_ROW_PADDING = 2

# UI Text and Labels
SELECT_FOLDER_TEXT = "Select Target Folder"
SELECT_FILE_TEXT = "Select Sample File"
CHANGE_FOLDER_TEXT = "Change Target Folder"
CHANGE_FILE_TEXT = "Change Sample File"
CREATE_BACKUP_TEXT = "Create Backup"
UNLOCK_PDFS_TEXT = "Unlock PDFs"

# UI Colors
TRANSPARENT_COLOR = "transparent"
HOVER_COLOR = "gray40"
TEXT_COLOR = "gray90"
BUILD_DATE_COLOR = "gray30"

# UI Fonts
FONT_FAMILY = "Arial"
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 28
