import os
import pikepdf
from tkinter import messagebox
from ..logging_config import ui_logger as logger
from ..exceptions import FileOperationError, ValidationError

def unlock_pdfs_in_folder(folder_path: str, parent_window=None) -> None:
    """
    Unlocks all PDFs in the specified folder assuming no password is needed.
    If a PDF is password-protected or an error occurs, it is skipped.
    Overwrites the original file when unlocking succeeds.
    
    Args:
        folder_path: Path to the folder containing PDFs to unlock
        parent_window: Optional parent window for message boxes
        
    Raises:
        ValidationError: If folder_path is not a valid directory
        FileOperationError: If file operations fail
    """
    logger.info(f"Starting PDF unlock operation in folder: {folder_path}")
    if not os.path.isdir(folder_path):
        logger.error(f"Invalid folder path: {folder_path}")
        raise ValidationError(f"Invalid folder path: {folder_path}")

    # Get list of PDF files (ensure full file path exists)
    pdf_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(folder_path, f))
    ]
    if not pdf_files:
        logger.warning("No PDF files found in folder")
        messagebox.showinfo("No PDFs Found", "There are no PDF files in the selected folder.", parent=parent_window)
        return

    logger.info(f"Found {len(pdf_files)} PDF files to process")
    # Ask user to confirm unlocking the files
    confirm = messagebox.askyesno("Confirm Unlock", f"Unlock {len(pdf_files)} file(s)?", parent=parent_window)
    if not confirm:
        logger.info("User cancelled PDF unlock operation")
        return

    unlocked_count = 0
    failed_files = []

    for filename in pdf_files:
        full_path = os.path.join(folder_path, filename)
        logger.debug(f"Processing PDF: {filename}")
        try:
            # Attempt to open and save the PDF without a password
            with pikepdf.open(full_path, allow_overwriting_input=True) as pdf:
                pdf.save(full_path)
            unlocked_count += 1
            logger.info(f"Successfully unlocked: {filename}")
        except pikepdf.PasswordError:
            # Password is required – add note to failed files
            logger.warning(f"Password required for: {filename}")
            failed_files.append(f"{filename} (password required)")
        except Exception as e:
            # Other errors – capture the exception message
            logger.error(f"Failed to unlock {filename}: {str(e)}", exc_info=True)
            failed_files.append(f"{filename} (error: {e})")

    # Prepare summary message
    summary = f"Unlocked {unlocked_count} file(s) successfully."
    if failed_files:
        summary += "\n\nThe following files could not be unlocked:\n" + "\n".join(failed_files)
        logger.warning(f"Unlock operation completed with failures: {len(failed_files)} files failed")
        messagebox.showwarning("Unlock Operation Completed", summary, parent=parent_window)
    else:
        logger.info("Unlock operation completed successfully")
        messagebox.showinfo("Unlock Operation Completed", summary, parent=parent_window)
