import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from ..constants import FRAME_PADDING, TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR, CONFIG_DIR_NAME, BACKUP_DIR_NAME, LOGS_DIR_NAME, DATABASE_DIR_NAME
from ..ui_utils import create_button
from ..utils import get_backup_destination_from_config, set_backup_destination_in_config, get_logs_destination_from_config, set_logs_destination_in_config, get_database_destination_from_config, set_database_destination_in_config, move_database_file

class SettingsFrame(ctk.CTkFrame):
    """
    Frame for user settings (e.g., backup destination, clear backups, etc.).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.backup_path = get_backup_destination_from_config()
        self.logs_path = get_logs_destination_from_config()
        self.database_path = get_database_destination_from_config()
        self._create_widgets()

    def _create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self, text="Settings", font=("Arial", 20, "bold"))
        title_label.pack(pady=(FRAME_PADDING, FRAME_PADDING // 2))

        # Backup folder row
        self._create_backup_folder_row()

        # Logs folder row
        self._create_logs_folder_row()

        # Database folder row
        self._create_database_folder_row()

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
        row_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT_COLOR)
        row_frame.pack(fill="x", padx=FRAME_PADDING, pady=(10, 5))

        # Header label (fixed width)
        header_label = ctk.CTkLabel(row_frame, text="Backups:", font=("Arial", 12, "bold"), width=80, anchor="w", fg_color=TRANSPARENT_COLOR)
        header_label.pack(side="left", padx=(0, 5))

        folder_text_frame = ctk.CTkFrame(row_frame, fg_color=TRANSPARENT_COLOR)
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
            text="Change Path",
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._on_change_backup_folder,
            width=90
        )
        self.change_backup_button.pack(side="left", padx=(10, 0))

        self.reset_backup_button = create_button(
            row_frame,
            text="Reset Path",
            command=self._on_reset_backup_folder,
            width=90
        )
        self.reset_backup_button.pack(side="left", padx=(10, 0))

        # Clear Backups button (icon only)
        clear_backup_btn = create_button(
            row_frame,
            text="🗑",
            command=self._on_clear_backups,
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR
        )
        clear_backup_btn.pack(side="left", padx=(10, 0))

    def _create_logs_folder_row(self):
        row_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT_COLOR)
        row_frame.pack(fill="x", padx=FRAME_PADDING, pady=(5, 5))

        # Header label (fixed width)
        header_label = ctk.CTkLabel(row_frame, text="Debug Logs:", font=("Arial", 12, "bold"), width=80, anchor="w", fg_color=TRANSPARENT_COLOR)
        header_label.pack(side="left", padx=(0, 5))

        folder_text_frame = ctk.CTkFrame(row_frame, fg_color=TRANSPARENT_COLOR)
        folder_text_frame.pack(side="left", fill="x", expand=True)

        self.open_logs_folder_button = create_button(
            folder_text_frame,
            text="📂",
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._open_logs_folder_in_explorer
        )
        self.open_logs_folder_button.pack(side="left")

        self.logs_entry = ctk.CTkEntry(folder_text_frame, state="readonly")
        self.logs_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self._update_logs_entry()

        self.change_logs_button = create_button(
            row_frame,
            text="Change Path",
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._on_change_logs_folder,
            width=90
        )
        self.change_logs_button.pack(side="left", padx=(10, 0))

        self.reset_logs_button = create_button(
            row_frame,
            text="Reset Path",
            command=self._on_reset_logs_folder,
            width=90
        )
        self.reset_logs_button.pack(side="left", padx=(10, 0))

        # Clear Logs button (icon only)
        clear_logs_btn = create_button(
            row_frame,
            text="🗑",
            command=self._on_clear_logs,
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR
        )
        clear_logs_btn.pack(side="left", padx=(10, 0))

    def _create_database_folder_row(self):
        row_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT_COLOR)
        row_frame.pack(fill="x", padx=FRAME_PADDING, pady=(5, 5))

        # Header label (fixed width)
        header_label = ctk.CTkLabel(row_frame, text="Database:", font=("Arial", 12, "bold"), width=80, anchor="w", fg_color=TRANSPARENT_COLOR)
        header_label.pack(side="left", padx=(0, 5))

        folder_text_frame = ctk.CTkFrame(row_frame, fg_color=TRANSPARENT_COLOR)
        folder_text_frame.pack(side="left", fill="x", expand=True)

        self.open_database_folder_button = create_button(
            folder_text_frame,
            text="📂",
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._open_database_folder_in_explorer
        )
        self.open_database_folder_button.pack(side="left")

        self.database_entry = ctk.CTkEntry(folder_text_frame, state="readonly")
        self.database_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self._update_database_entry()

        self.change_database_button = create_button(
            row_frame,
            text="Change Path",
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._on_change_database_folder,
            width=90
        )
        self.change_database_button.pack(side="left", padx=(10, 0))

        self.reset_database_button = create_button(
            row_frame,
            text="Reset Path",
            command=self._on_reset_database_folder,
            width=90
        )
        self.reset_database_button.pack(side="left", padx=(10, 0))

        # Empty placeholder for alignment (same width as trash button)
        placeholder = ctk.CTkLabel(row_frame, text="", width=30)
        placeholder.pack(side="left", padx=(10, 0))

    def _update_backup_entry(self):
        self.backup_entry.configure(state="normal")
        self.backup_entry.delete(0, "end")
        self.backup_entry.insert(0, str(self.backup_path))
        self.backup_entry.configure(state="readonly")

    def _update_logs_entry(self):
        self.logs_entry.configure(state="normal")
        self.logs_entry.delete(0, "end")
        self.logs_entry.insert(0, str(self.logs_path))
        self.logs_entry.configure(state="readonly")

    def _update_database_entry(self):
        self.database_entry.configure(state="normal")
        self.database_entry.delete(0, "end")
        self.database_entry.insert(0, str(self.database_path))
        self.database_entry.configure(state="readonly")

    def _open_backup_folder_in_explorer(self):
        if self.backup_path and os.path.isdir(self.backup_path):
            try:
                from ..utils import open_in_file_explorer
                open_in_file_explorer(self.backup_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
        else:
            messagebox.showwarning("Folder Not Found", "The backup folder does not exist.")

    def _open_logs_folder_in_explorer(self):
        if self.logs_path and os.path.isdir(self.logs_path):
            try:
                from ..utils import open_in_file_explorer
                open_in_file_explorer(self.logs_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
        else:
            messagebox.showwarning("Folder Not Found", "The logs folder does not exist.")

    def _open_database_folder_in_explorer(self):
        if self.database_path and os.path.isdir(self.database_path):
            try:
                from ..utils import open_in_file_explorer
                open_in_file_explorer(self.database_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
        else:
            messagebox.showwarning("Folder Not Found", "The database folder does not exist.")

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

    def _on_change_logs_folder(self):
        new_folder = filedialog.askdirectory(title="Select New Logs Folder")
        if new_folder:
            set_logs_destination_in_config(new_folder)
            self.logs_path = new_folder
            self._update_logs_entry()
            self.parent.toast_manager.show_toast(f"Logs folder set to: {new_folder}")

    def _on_reset_logs_folder(self):
        from pathlib import Path
        default_path = str(Path.home() / CONFIG_DIR_NAME / LOGS_DIR_NAME)
        set_logs_destination_in_config(default_path)
        self.logs_path = default_path
        self._update_logs_entry()
        self.parent.toast_manager.show_toast(f"Logs folder reset to default: {default_path}")

    def _on_change_database_folder(self):
        new_folder = filedialog.askdirectory(title="Select New Database Folder")
        if new_folder:
            # Get current database file path
            from pathlib import Path
            current_db_file = Path(self.database_path) / "clients.db"
            new_db_file = Path(new_folder) / "clients.db"
            
            # Check if database file exists and move it
            if current_db_file.exists():
                if move_database_file(current_db_file, new_db_file):
                    set_database_destination_in_config(new_folder)
                    self.database_path = new_folder
                    self._update_database_entry()
                    self.parent.toast_manager.show_toast(f"Database moved to: {new_folder}")
                else:
                    messagebox.showerror("Error", "Failed to move database file. Please ensure the new location is accessible.")
            else:
                # Database file doesn't exist, just update config
                set_database_destination_in_config(new_folder)
                self.database_path = new_folder
                self._update_database_entry()
                self.parent.toast_manager.show_toast(f"Database folder set to: {new_folder}")

    def _on_reset_database_folder(self):
        from pathlib import Path
        default_path = str(Path.home() / CONFIG_DIR_NAME / DATABASE_DIR_NAME)
        
        # Get current database file path
        current_db_file = Path(self.database_path) / "clients.db"
        new_db_file = Path(default_path) / "clients.db"
        
        # Check if database file exists and move it
        if current_db_file.exists():
            if move_database_file(current_db_file, new_db_file):
                set_database_destination_in_config(default_path)
                self.database_path = default_path
                self._update_database_entry()
                self.parent.toast_manager.show_toast(f"Database moved to default: {default_path}")
            else:
                messagebox.showerror("Error", "Failed to move database file to default location.")
        else:
            # Database file doesn't exist, just update config
            set_database_destination_in_config(default_path)
            self.database_path = default_path
            self._update_database_entry()
            self.parent.toast_manager.show_toast(f"Database folder reset to default: {default_path}")

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

    def _on_clear_logs(self):
        import glob
        from pathlib import Path
        logs_dir = Path(self.logs_path)
        if not logs_dir.is_dir():
            self.parent.toast_manager.show_toast("Logs folder does not exist.")
            return
        log_files = list(logs_dir.glob("*.log"))
        num_files = len(log_files)
        if num_files == 0:
            self.parent.toast_manager.show_toast("No logs to clear.")
            return
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Clear Logs",
            f"Are you sure you want to delete all {num_files} log(s) in this folder? This cannot be undone."
        )
        if confirm:
            deleted = 0
            for f in log_files:
                try:
                    f.unlink()
                    deleted += 1
                except Exception:
                    pass
            self.parent.toast_manager.show_toast(f"Deleted {deleted} log(s).")

    def _on_about(self):
        from tkinter import messagebox
        from ..build_info import get_build_info, format_build_string
        
        # Get build information
        build_info = get_build_info()
        
        # Create the about message
        about_text = (
            "BatchRename\n"
            "A tool for bulk renaming files and other utilities.\n\n"
            "Developed by Bryce Pagel for Barron | Pagel, PLLC.\n\n"
            f"{format_build_string()}"
        )
        
        # Add additional build details if available
        if build_info['commit_hash'] and build_info['commit_hash'] != 'unknown':
            about_text += f"\n\nCommit: {build_info['commit_hash']}"
        
        if build_info['branch_name'] and build_info['branch_name'] not in ['main', 'master', 'unknown']:
            about_text += f"\nBranch: {build_info['branch_name']}"
        
        messagebox.showinfo("About", about_text) 