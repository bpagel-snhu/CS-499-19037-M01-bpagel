# batch_renamer/ui/main_window.py

import customtkinter as ctk
from tkinter import messagebox
from .toast_manager import ToastManager
from .folder_file_select_frame import FolderFileSelectFrame
from .main_menu_frame import MainMenuFrame  # NEW IMPORT
from ..logging_config import ui_logger as logger
from ..constants import (
    WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, BUILD_DATE_COLOR, FRAME_PADDING
)
from ..folder_file_logic import FolderFileManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class BatchRename(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Set window icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'batchRename.ico')
            self.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Failed to set window icon: {e}")
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

        self.current_frame = None
        self._build_date_label = None
        self.show_main_menu()
        logger.info("Main window initialization complete")

    def _show_build_date_label(self):
        from batch_renamer.ui.main_menu_frame import get_build_date
        if self._build_date_label:
            self._build_date_label.destroy()
        self._build_date_label = ctk.CTkLabel(
            self,
            text=f"Build: {get_build_date()}",
            font=("Arial", 10),
            text_color=BUILD_DATE_COLOR,
            fg_color="transparent"
        )
        self._build_date_label.place(relx=1.0, rely=1.0, anchor="se", x=-1, y=10)

    def _hide_build_date_label(self):
        if self._build_date_label:
            self._build_date_label.destroy()
            self._build_date_label = None

    def show_main_menu(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        self.current_frame = MainMenuFrame(parent=self, main_window=self)
        self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
        self._show_build_date_label()
        logger.debug("Main menu frame shown")

    def show_folder_file_select(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        self.current_frame = FolderFileSelectFrame(parent=self)
        self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
        self._hide_build_date_label()
        logger.debug("Folder/File selection frame shown")

    def show_toast(self, message: str):
        """
        Convenience method to show a toast via toast_manager.
        
        Args:
            message: The message to display in the toast
        """
        logger.debug(f"Showing toast message: {message}")
        self.toast_manager.show_toast(message)


