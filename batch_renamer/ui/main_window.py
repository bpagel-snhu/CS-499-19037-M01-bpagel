# batch_renamer/ui/main_window.py

import customtkinter as ctk
from tkinter import messagebox
from .toast_manager import ToastManager
from .folder_file_select_frame import FolderFileSelectFrame
from .main_menu_frame import MainMenuFrame  # NEW IMPORT
from ..logging_config import ui_logger as logger
from ..constants import (
    WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, BUILD_DATE_COLOR, FRAME_PADDING,
    FONT_FAMILY, FONT_SIZE_SMALL, FONT_SIZE_NORMAL
)
from ..folder_file_logic import FolderFileManager
from ..utils import create_button

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
        self._back_button = None
        self._status_label = None
        self.show_main_menu()
        logger.info("Main window initialization complete")

    def _show_build_date_label(self):
        from batch_renamer.ui.main_menu_frame import get_build_date
        if self._build_date_label:
            self._build_date_label.destroy()
        self._build_date_label = ctk.CTkLabel(
            self,
            text=f"Build: {get_build_date()}",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=BUILD_DATE_COLOR,
            fg_color="transparent"
        )
        self._build_date_label.place(relx=1.0, rely=1.0, anchor="se", x=-1, y=10)

    def _hide_build_date_label(self):
        if self._build_date_label:
            self._build_date_label.destroy()
            self._build_date_label = None

    def _show_back_button(self):
        """Show the back button in the bottom left corner."""
        if self._back_button:
            self._back_button.destroy()

        self._back_button = create_button(
            self,
            text="← Back to Menu",
            command=self.show_main_menu,
            width=100,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            text_color=("gray50", "gray50")
        )
        self._back_button.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

    def _hide_back_button(self):
        """Hide the back button."""
        if self._back_button:
            self._back_button.destroy()
            self._back_button = None

    def _show_status_label(self, tool_name: str):
        """Show the status label in the bottom center."""
        if self._status_label:
            self._status_label.destroy()

        self._status_label = ctk.CTkLabel(
            self,
            text=f"{tool_name}",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            fg_color=("gray20", "gray20"),
            text_color=("gray70", "gray70"),
            corner_radius=5,
            width=150,
            height=30
        )
        self._status_label.place(relx=0.5, rely=1.0, anchor="s", x=0, y=-10)

    def _hide_status_label(self):
        """Hide the status label."""
        if self._status_label:
            self._status_label.destroy()
            self._status_label = None

    def show_main_menu(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        self.current_frame = MainMenuFrame(parent=self, main_window=self)
        self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
        self._show_build_date_label()
        self._hide_back_button()  # Hide back button on main menu
        self._hide_status_label()  # Hide status label on main menu
        logger.debug("Main menu frame shown")

    def show_folder_file_select(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        self.current_frame = FolderFileSelectFrame(parent=self)
        self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
        self._hide_build_date_label()
        self._show_back_button()  # Show back button when in renamer tool
        self._show_status_label("Bulk Rename")  # Show status label for renamer tool
        logger.debug("Folder/File selection frame shown")

    def show_pdf_unlock(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        from ..tools.pdf_unlock.pdf_unlock_frame import PDFUnlockFrame
        self.current_frame = PDFUnlockFrame(parent=self)
        self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
        self._hide_build_date_label()
        self._show_back_button()  # Show back button when in PDF unlock tool
        self._show_status_label("PDF Unlock")  # Show status label for PDF unlock tool
        logger.debug("PDF unlock frame shown")

    def show_toast(self, message: str):
        """
        Convenience method to show a toast via toast_manager.
        
        Args:
            message: The message to display in the toast
        """
        logger.debug(f"Showing toast message: {message}")
        self.toast_manager.show_toast(message)
