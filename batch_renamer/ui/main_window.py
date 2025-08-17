# batch_renamer/ui/main_window.py

import customtkinter as ctk
from tkinter import messagebox
from .toast_manager import ToastManager
from .progress_manager import ProgressManager
from .folder_file_select_frame import FolderFileSelectFrame
from .main_menu_frame import MainMenuFrame  # NEW IMPORT
from ..logging_config import ui_logger as logger
from ..constants import (
    WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, BUILD_DATE_COLOR, FRAME_PADDING,
    FONT_FAMILY, FONT_SIZE_SMALL, FONT_SIZE_NORMAL
)
from ..folder_file_logic import FolderFileManager
from ..ui_utils import create_button
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class BatchRename(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Set window icon
        try:
            import os
            if sys.platform.startswith("win"):
                icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'batchRename.ico')
                self.iconbitmap(icon_path)
            else:
                import tkinter as tk
                icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'batchRename.png')
                icon_img = tk.PhotoImage(file=icon_path)
                self.iconphoto(False, icon_img)
        except Exception as e:
            logger.warning(f"Failed to set window icon: {e}")
        logger.info("Initializing main window")

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)

        # Center the window on the screen
        self.center_window()

        # Set minimum window size
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Make window resizable
        self.resizable(True, True)

        # Initialize the folder/file manager
        self.manager = FolderFileManager()

        # Toast manager
        self.toast_manager = ToastManager(self)
        logger.debug("Toast manager initialized")

        # Progress manager
        self.progress_manager = ProgressManager(self)
        logger.debug("Progress manager initialized")

        self.current_frame = None
        self._build_date_label = None
        self._back_button = None
        self._status_label = None
        self.show_main_menu()
        logger.info("Main window initialization complete")

    def center_window(self):
        """
        Center the window on the screen.
        """
        # Update the window to ensure geometry is applied
        self.update_idletasks()
        
        # Get the screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Parse the original window size from WINDOW_SIZE constant
        width, height = map(int, WINDOW_SIZE.split('x'))
        
        # Calculate the position to center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set the window position while preserving the original size
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _show_build_date_label(self):
        from batch_renamer.build_info import format_build_string
        if self._build_date_label:
            self._build_date_label.destroy()
        self._build_date_label = ctk.CTkLabel(
            self,
            text=format_build_string(),
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

    def show_settings(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        from .settings_frame import SettingsFrame
        self.current_frame = SettingsFrame(parent=self)
        self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
        self._hide_build_date_label()
        self._show_back_button()
        self._show_status_label("Settings")
        logger.debug("Settings frame shown")

    def show_database_logging(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        from ..tools.database_logging.database_frame import DatabaseFrame
        self.current_frame = DatabaseFrame(parent=self, main_window=self)
        self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
        self._hide_build_date_label()
        self._show_back_button()  # Show back button when in database tool
        self._show_status_label("Database Logging")  # Show status label for database tool
        logger.debug("Database logging frame shown")

    def show_toast(self, message: str):
        """
        Convenience method to show a toast via toast_manager.
        
        Args:
            message: The message to display in the toast
        """
        logger.debug(f"Showing toast message: {message}")
        self.toast_manager.show_toast(message)
        
    def run_with_progress(self, operation, title: str = "Processing...", 
                         determinate: bool = True, can_cancel: bool = True):
        """
        Convenience method to run an operation with progress bar.
        
        Args:
            operation: The function to run (should accept a progress_callback parameter)
            title: Title for the progress bar
            determinate: Whether to show determinate progress
            can_cancel: Whether to show cancel button
            
        Returns:
            The result of the operation, or None if cancelled
        """
        return self.progress_manager.run_with_progress(operation, title, determinate, can_cancel)
