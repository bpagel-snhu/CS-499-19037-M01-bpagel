# batch_renamer/ui/main_window.py

import customtkinter as ctk
from tkinter import messagebox
from .toast_manager import ToastManager
from .folder_file_select_frame import FolderFileSelectFrame

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class BatchRename(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bulk File Renamer")
        self.geometry("800x450")

        # Shared state
        self.full_folder_path = None
        self.folder_name = None
        self.show_full_path = False

        self.full_file_path = None
        self.file_name = None
        self.show_full_file_path = False

        # Toast manager
        self.toast_manager = ToastManager(self)

        # Folder/File selection frame
        self.folder_file_select_frame = FolderFileSelectFrame(parent=self)
        self.folder_file_select_frame.pack(padx=20, pady=20, fill="x")

    def show_toast(self, message: str):
        """Convenience method to show a toast via toast_manager."""
        self.toast_manager.show_toast(message)


