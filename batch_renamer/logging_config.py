"""
Logging configuration for the batch_renamer package.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


def setup_logging(log_level=logging.INFO):
    """
    Configure logging for the application.
    
    Creates log files in the user's Documents folder under 'BatchRenamer/logs'.
    Configures both file and console logging.
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
    """
    # Create logs directory in user's Documents
    log_dir = Path.home() / "Documents" / "BatchRenamer" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"batch_renamer_{timestamp}.log"

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # File handler - detailed logging
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler - less detailed
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only show warnings and above in console
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Log rotation - keep last 30 days of logs
    log_rotation = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    log_rotation.setFormatter(file_formatter)
    logger.addHandler(log_rotation)

    # Log startup information
    logger.info("Logging system initialized")
    logger.info(f"Log file: {log_file}")

    return logger


# Create module-level loggers
ui_logger = logging.getLogger('batch_renamer.ui')
rename_logger = logging.getLogger('batch_renamer.rename')
backup_logger = logging.getLogger('batch_renamer.backup')
