import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from ..constants import FRAME_PADDING, BUTTON_WIDTH, TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR, CONFIG_DIR_NAME, BACKUP_DIR_NAME
from ..utils import create_button, get_backup_destination_from_config, set_backup_destination_in_config

class SettingsFrame(ctk.CTkFrame):
    """
    Frame for user settings (e.g., backup destination, clear backups, etc.).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.backup_path = get_backup_destination_from_config()
        self._create_widgets()

    def _create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self, text="Settings", font=("Arial", 20, "bold"))
        title_label.pack(pady=(FRAME_PADDING, FRAME_PADDING // 2))

        # Backup folder row
        self._create_backup_folder_row()

        # Clear Backups button (below backup folder row)
        clear_btn = create_button(
            self,
            text="Clear Backups",
            command=self._on_clear_backups,
            width=BUTTON_WIDTH,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR
        )
        clear_btn.pack(pady=(0, 10))

        # About button (bottom right)
        about_btn = create_button(
            self,
            text="About",
            command=self._on_about,
            width=100,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR
        )
        about_btn.place(relx=1.0, rely=1.0, anchor="se", x=-FRAME_PADDING, y=-FRAME_PADDING)

    def _create_backup_folder_row(self):
        row_frame = ctk.CTkFrame(self)
        row_frame.pack(fill="x", padx=FRAME_PADDING, pady=(10, 10))

        folder_text_frame = ctk.CTkFrame(row_frame)
        folder_text_frame.pack(side="left", fill="x", expand=True)

        self.open_folder_button = create_button(
            folder_text_frame,
            text="📂",
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._open_backup_folder_in_explorer
        )
        self.open_folder_button.pack(side="left")

        self.backup_entry = ctk.CTkEntry(folder_text_frame, state="readonly")
        self.backup_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self._update_backup_entry()

        self.change_backup_button = create_button(
            row_frame,
            text="Change Backup Folder",
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._on_change_backup_folder,
            width=BUTTON_WIDTH
        )
        self.change_backup_button.pack(side="left", padx=(10, 0))

        self.reset_backup_button = create_button(
            row_frame,
            text="Reset to Default",
            command=self._on_reset_backup_folder,
            width=BUTTON_WIDTH
        )
        self.reset_backup_button.pack(side="left", padx=(10, 0))

    def _update_backup_entry(self):
        self.backup_entry.configure(state="normal")
        self.backup_entry.delete(0, "end")
        self.backup_entry.insert(0, str(self.backup_path))
        self.backup_entry.configure(state="readonly")

    def _open_backup_folder_in_explorer(self):
        if self.backup_path and os.path.isdir(self.backup_path):
            try:
                from ..utils import open_in_file_explorer
                open_in_file_explorer(self.backup_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
        else:
            messagebox.showwarning("Folder Not Found", "The backup folder does not exist.")

    def _on_change_backup_folder(self):
        new_folder = filedialog.askdirectory(title="Select New Backup Folder")
        if new_folder:
            set_backup_destination_in_config(new_folder)
            self.backup_path = new_folder
            self._update_backup_entry()
            self.parent.toast_manager.show_toast(f"Backup folder set to: {new_folder}")

    def _on_reset_backup_folder(self):
        from pathlib import Path
        default_path = str(Path.home() / CONFIG_DIR_NAME / BACKUP_DIR_NAME)
        set_backup_destination_in_config(default_path)
        self.backup_path = default_path
        self._update_backup_entry()
        self.parent.toast_manager.show_toast(f"Backup folder reset to default: {default_path}")

    def _on_clear_backups(self):
        import glob
        from pathlib import Path
        backup_dir = Path(self.backup_path)
        if not backup_dir.is_dir():
            self.parent.toast_manager.show_toast("Backup folder does not exist.")
            return
        backup_files = list(backup_dir.glob("*.zip"))
        num_files = len(backup_files)
        if num_files == 0:
            self.parent.toast_manager.show_toast("No backups to clear.")
            return
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Clear Backups",
            f"Are you sure you want to delete all {num_files} backup(s) in this folder? This cannot be undone."
        )
        if confirm:
            deleted = 0
            for f in backup_files:
                try:
                    f.unlink()
                    deleted += 1
                except Exception:
                    pass
            self.parent.toast_manager.show_toast(f"Deleted {deleted} backup(s).")

    def _on_about(self):
        from tkinter import messagebox
        messagebox.showinfo(
            "About",
            "BatchRename\nA tool for bulk renaming files and other utilities.\n\nDeveloped by Bryce Pagel for Barron | Pagel, PLLC."
        ) 