"""
Logging configuration for the batch_renamer package.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from .constants import CONFIG_DIR_NAME, LOGS_DIR_NAME, LOG_RETENTION_COUNT
from .utils import get_logs_directory, get_logs_destination_from_config


def cleanup_old_logs(log_dir: Path, keep_count: int = 10) -> None:
    """
    Clean up old log files, keeping only the most recent ones.
    
    Args:
        log_dir: Directory containing log files
        keep_count: Number of most recent log files to keep (default: 10)
    """
    # Create a temporary logger for cleanup messages
    cleanup_logger = logging.getLogger('batch_renamer.cleanup')
    
    try:
        # Get all log files in the directory
        log_files = list(log_dir.glob("batch_renamer_*.log"))
        
        if len(log_files) <= keep_count:
            return  # No cleanup needed
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Delete the oldest files
        files_to_delete = log_files[keep_count:]
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                cleanup_logger.warning(f"Failed to delete old log file {file_path.name}: {e}")
        
        if deleted_count > 0:
            cleanup_logger.info(f"Cleaned up {deleted_count} old log files, keeping {keep_count} most recent")
                
    except Exception as e:
        cleanup_logger.error(f"Error during log cleanup: {e}")


def setup_logging(log_level=logging.INFO):
    """
    Configure logging for the application.
    
    Creates log files in the user's home directory under '.bpfu/logs'.
    Configures both file and console logging.
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
    """
    # Create logs directory in user's home directory under .bpfu
    log_dir = get_logs_destination_from_config()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean up old log files before creating new ones
    cleanup_old_logs(log_dir, LOG_RETENTION_COUNT)

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
