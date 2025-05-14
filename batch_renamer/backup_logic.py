# batch_renamer/backup_logic.py

import subprocess
from tkinter import messagebox
from pathlib import Path
from .constants import BACKUP_DIR_NAME, BACKUP_PREFIX, BACKUP_EXTENSION
from .utils import get_backup_directory, ensure_directory_exists
from .exceptions import BackupError, ValidationError
from .logging_config import backup_logger as logger

def create_backup_interactive(folder_path):
    """
    Does the entire backup flow interactively:
      1) Check if folder is valid
      2) Check for existing .zip and ask overwrite
      3) Call create_folder_backup
      4) Show success/failure messageboxes
    """
    logger.info(f"Starting interactive backup for folder: {folder_path}")
    
    try:
        if not folder_path or not Path(folder_path).is_dir():
            logger.error(f"Invalid folder path: {folder_path}")
            raise ValidationError("No valid folder selected.")
            
        backup_dir = get_backup_directory()
        folder_name = Path(folder_path).name
        zip_filename = f"{BACKUP_PREFIX}{folder_name}{BACKUP_EXTENSION}"
        zip_path = backup_dir / zip_filename
        
        logger.debug(f"Backup will be created at: {zip_path}")

        if zip_path.exists():
            logger.info(f"Existing backup found at {zip_path}")
            answer = messagebox.askyesno(
                "Overwrite Existing Backup?",
                f"A backup already exists:\n{zip_path}\n\nOverwrite it?"
            )
            if not answer:
                logger.info("User chose not to overwrite existing backup")
                return

        try:
            final_path = create_folder_backup(folder_path)
            logger.info(f"Backup created successfully at: {final_path}")
            messagebox.showinfo("Backup Created", f"Successfully created backup:\n{final_path}")
        except Exception as e:
            logger.exception("Failed to create backup")
            messagebox.showerror("Backup Error", str(e))
            
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        messagebox.showerror("Backup Error", str(e))
    except Exception as e:
        logger.exception("Unexpected error during backup")
        messagebox.showerror("Backup Error", f"An unexpected error occurred: {e}")

def create_folder_backup(folder_path):
    """
    Creates a backup of the specified folder using 7-Zip.
    
    Args:
        folder_path: Path to the folder to backup
        
    Returns:
        str: Path to the created backup file
        
    Raises:
        ValidationError: If the folder path is invalid
        BackupError: If the backup operation fails
    """
    logger.info(f"Creating backup for folder: {folder_path}")
    
    if not Path(folder_path).is_dir():
        error_msg = f"'{folder_path}' is not a valid folder path."
        logger.error(error_msg)
        raise ValidationError(error_msg)

    backup_dir = get_backup_directory()
    folder_name = Path(folder_path).name
    zip_filename = f"{BACKUP_PREFIX}{folder_name}{BACKUP_EXTENSION}"
    zip_path = backup_dir / zip_filename

    logger.debug(f"Using 7z to create backup at: {zip_path}")
    
    cmd = [
        "7z", "a",
        str(zip_path),
        folder_path,
        "-r"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.debug(f"7z output: {result.stdout}")
        return str(zip_path)
    except FileNotFoundError as e:
        error_msg = "Could not find '7z' executable. Ensure 7-Zip is on your PATH."
        logger.error(error_msg)
        raise BackupError(error_msg, original_error=e)
    except subprocess.CalledProcessError as e:
        error_msg = f"7z failed to create backup: {e.stderr}"
        logger.error(f"{error_msg}\nCommand output: {e.stdout}")
        raise BackupError(error_msg, original_error=e)

