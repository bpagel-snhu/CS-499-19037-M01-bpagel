import os
import pikepdf
from tkinter import messagebox

def unlock_pdfs_in_folder(folder_path, parent_window=None):
    """
    Unlocks all PDFs in the specified folder assuming no password is needed.
    If a PDF is password-protected or an error occurs, it is skipped.
    Overwrites the original file when unlocking succeeds.
    """
    if not os.path.isdir(folder_path):
        raise ValueError("Provided folder path is not valid.")

    # Get list of PDF files (ensure full file path exists)
    pdf_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(folder_path, f))
    ]
    if not pdf_files:
        messagebox.showinfo("No PDFs Found", "There are no PDF files in the selected folder.", parent=parent_window)
        return

    # Ask user to confirm unlocking the files
    confirm = messagebox.askyesno("Confirm Unlock", f"Unlock {len(pdf_files)} file(s)?", parent=parent_window)
    if not confirm:
        return

    unlocked_count = 0
    failed_files = []

    for filename in pdf_files:
        full_path = os.path.join(folder_path, filename)
        try:
            # Attempt to open and save the PDF without a password
            with pikepdf.open(full_path, allow_overwriting_input=True) as pdf:
                pdf.save(full_path)
            unlocked_count += 1
        except pikepdf.PasswordError:
            # Password is required – add note to failed files
            failed_files.append(f"{filename} (password required)")
        except Exception as e:
            # Other errors – capture the exception message
            failed_files.append(f"{filename} (error: {e})")

    # Prepare summary message
    summary = f"Unlocked {unlocked_count} file(s) successfully."
    if failed_files:
        summary += "\n\nThe following files could not be unlocked:\n" + "\n".join(failed_files)
        messagebox.showwarning("Unlock Operation Completed", summary, parent=parent_window)
    else:
        messagebox.showinfo("Unlock Operation Completed", summary, parent=parent_window)
