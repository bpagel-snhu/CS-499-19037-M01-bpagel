# batch_renamer/ui/main_window.py

import customtkinter as ctk
from tkinter import messagebox
from .toast_manager import ToastManager
from .folder_file_select_frame import FolderFileSelectFrame
from ..logging_config import ui_logger as logger
from ..constants import (
    WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
)
from ..folder_file_logic import FolderFileManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class BatchRename(ctk.CTk):
    def __init__(self):
        super().__init__()
        logger.info("Initializing main window")

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        
        # Set minimum window size
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Make window resizable
        self.resizable(True, True)

        # Initialize the folder/file manager
        self.manager = FolderFileManager()

        # Toast manager
        self.toast_manager = ToastManager(self)
        logger.debug("Toast manager initialized")

        # Folder/File selection frame
        self.folder_file_select_frame = FolderFileSelectFrame(parent=self)
        self.folder_file_select_frame.pack(padx=20, pady=20, fill="both", expand=True)
        logger.debug("Folder/File selection frame initialized")

        logger.info("Main window initialization complete")

    def show_toast(self, message: str):
        """
        Convenience method to show a toast via toast_manager.
        
        Args:
            message: The message to display in the toast
        """
        logger.debug(f"Showing toast message: {message}")
        self.toast_manager.show_toast(message)


