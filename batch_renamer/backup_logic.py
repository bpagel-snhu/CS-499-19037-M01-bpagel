# batch_renamer/backup_logic.py

import os
import subprocess
from tkinter import messagebox

def create_backup_interactive(folder_path):
    """
    Does the entire backup flow interactively:
      1) Check if folder is valid
      2) Check for existing .zip and ask overwrite
      3) Call create_folder_backup
      4) Show success/failure messageboxes
    """
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showerror("Backup Error", "No valid folder selected.")
        return

    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    backup_dir = os.path.join(downloads_dir, "Renamer Backups")
    folder_name = os.path.basename(folder_path)
    zip_filename = f"Backup_{folder_name}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)

    if os.path.exists(zip_path):
        answer = messagebox.askyesno(
            "Overwrite Existing Backup?",
            f"A backup already exists:\n{zip_path}\n\nOverwrite it?"
        )
        if not answer:
            return

    try:
        final_path = create_folder_backup(folder_path)
        messagebox.showinfo("Backup Created", f"Successfully created backup:\n{final_path}")
    except Exception as e:
        messagebox.showerror("Backup Error", str(e))

def create_folder_backup(folder_path):
    if not os.path.isdir(folder_path):
        raise ValueError(f"'{folder_path}' is not a valid folder path.")

    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    backup_dir = os.path.join(downloads_dir, "Renamer Backups")
    os.makedirs(backup_dir, exist_ok=True)

    folder_name = os.path.basename(folder_path)
    zip_filename = f"Backup_{folder_name}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)

    cmd = [
        "7z", "a",
        zip_path,
        folder_path,
        "-r"
    ]

    print("DEBUG: folder_path =", folder_path)
    print("DEBUG: zip_path =", zip_path)
    print("DEBUG: cmd =", cmd)

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise EnvironmentError(
            "Could not find '7z' executable. Ensure 7-Zip is on your PATH."
        )
    except subprocess.CalledProcessError as e:
        # Print out any stderr to see if 7-Zip gave a message
        print("DEBUG: CalledProcessError stderr:", e.stderr)
        raise RuntimeError(f"7z failed to create backup: {e}")

    return zip_path

