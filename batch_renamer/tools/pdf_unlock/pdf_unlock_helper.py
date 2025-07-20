import os
import pikepdf
import tempfile
import shutil
from tkinter import messagebox
from ...logging_config import ui_logger as logger
from ...exceptions import FileOperationError, ValidationError


def unlock_pdfs_in_folder(folder_path: str, parent_window=None) -> None:
    """
    Removes security restrictions from PDFs in the specified folder by creating new PDFs
    that preserve the visual content and text recognition while removing:
    - Digital signatures
    - Edit restrictions
    - Document permissions
    - Form fields
    - Interactive elements
    
    The resulting PDFs will be fully editable and suitable for bates numbering and redactions.
    Overwrites the original file when unlocking succeeds.
    
    Args:
        folder_path: Path to the folder containing PDFs to unlock
        parent_window: Optional parent window for message boxes
        
    Raises:
        ValidationError: If folder_path is not a valid directory
        FileOperationError: If file operations fail
    """
    logger.info(f"Starting PDF security removal operation in folder: {folder_path}")
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
    confirm = messagebox.askyesno("Confirm Security Removal",
                                  f"Remove security restrictions from {len(pdf_files)} file(s)?\n\n"
                                  "This will remove digital signatures, edit restrictions, and other security features. The document's visual quality and text recognition will be preserved.\n\n"
                                  "This cannot be undone.",
                                  parent=parent_window)
    if not confirm:
        logger.info("User cancelled PDF security removal operation")
        return

    unlocked_count = 0
    failed_files = []

    for filename in pdf_files:
        full_path = os.path.join(folder_path, filename)
        logger.debug(f"Processing PDF: {filename}")
        try:
            # Create a temporary file for saving
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_path = temp_file.name

            # Open the source PDF and create a new PDF
            with pikepdf.open(full_path) as src_pdf:
                with pikepdf.Pdf.new() as dst_pdf:
                    # Copy each page to the new PDF
                    for page in src_pdf.pages:
                        dst_pdf.pages.append(page)

                    # Save the new PDF
                    dst_pdf.save(temp_path)

            # Move the temporary file over the original
            shutil.move(temp_path, full_path)

            unlocked_count += 1
            logger.info(f"Successfully removed security from: {filename}")
        except pikepdf.PasswordError:
            # Password is required – add note to failed files
            logger.warning(f"Password required for: {filename}")
            failed_files.append(f"{filename} (password required)")
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception as e:
            # Other errors – capture the exception message
            logger.error(f"Failed to remove security from {filename}: {str(e)}", exc_info=True)
            failed_files.append(f"{filename} (error: {e})")
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    # Prepare summary message
    summary = f"Removed security from {unlocked_count} file(s) successfully."
    if failed_files:
        summary += "\n\nThe following files could not be processed:\n" + "\n".join(failed_files)
        logger.warning(f"Security removal operation completed with failures: {len(failed_files)} files failed")
        messagebox.showwarning("Security Removal Completed", summary, parent=parent_window)
    else:
        logger.info("Security removal operation completed successfully")
        messagebox.showinfo("Security Removal Completed", summary, parent=parent_window)
