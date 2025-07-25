# batch_renamer/tools/pdf_unlock/pdf_unlock_frame.py

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from ...logging_config import ui_logger as logger
from ...constants import (
    FRAME_PADDING, BUTTON_WIDTH, TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR
)
from ...utils import copy_to_clipboard, create_button
from .pdf_unlock_helper import unlock_pdfs_in_folder
from ...exceptions import FileOperationError, ValidationError


class PDFUnlockFrame(ctk.CTkFrame):
    """
    Frame for the PDF unlock tool that allows users to select a folder
    and unlock PDFs within that folder.
    """

    def __init__(self, parent):
        super().__init__(parent)
        logger.info("Initializing PDFUnlockFrame")
        self.parent = parent

        # State
        self.selected_folder = None

        # UI Components
        self.select_folder_button = None
        self.folder_header_frame = None
        self.folder_copy_button = None
        self.folder_entry = None
        self.unlock_button = None

        # Show the "Select Folder" button initially
        self._create_select_folder_button()
        logger.info("PDFUnlockFrame initialization complete")

    def _create_select_folder_button(self):
        """Creates the 'Select Folder' button with padding."""
        logger.debug("Creating select folder button")
        self.select_folder_button = create_button(
            self,
            text="Select Folder with PDFs",
            command=self._on_select_folder
        )
        self.select_folder_button.pack(padx=FRAME_PADDING, pady=(FRAME_PADDING, FRAME_PADDING))

    def _on_select_folder(self):
        """After user picks a folder, show folder info and unlock button."""
        logger.info("Opening folder selection dialog")
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            logger.info(f"Folder selected: {folder_selected}")
            
            # Update state
            self.selected_folder = folder_selected

            # Hide 'Select Folder' button
            self.select_folder_button.pack_forget()

            # Create folder UI
            self._create_folder_header()
            self._create_unlock_button()
            logger.info("Folder selection UI updated")

    def _create_folder_header(self):
        """Displays folder info and copy button."""
        logger.debug("Creating folder header")
        self._destroy_folder_header()

        self.folder_header_frame = ctk.CTkFrame(self)
        self.folder_header_frame.pack(fill="x", padx=FRAME_PADDING, pady=(10, 10))

        folder_text_frame = ctk.CTkFrame(self.folder_header_frame)
        folder_text_frame.pack(side="left", fill="x", expand=True)

        self.folder_copy_button = create_button(
            folder_text_frame,
            text="📂",
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._open_folder_in_explorer
        )
        self.folder_copy_button.pack(side="left")

        self.folder_entry = ctk.CTkEntry(folder_text_frame, state="readonly")
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self._update_folder_entry()
        logger.debug("Folder header created successfully")

    def _update_folder_entry(self):
        """Update the folder entry display text."""
        if self.selected_folder:
            # Show relative path if possible, otherwise full path
            try:
                relative_path = os.path.relpath(self.selected_folder)
                if len(relative_path) < len(self.selected_folder):
                    display_text = relative_path
                else:
                    display_text = self.selected_folder
            except ValueError:
                display_text = self.selected_folder
        else:
            display_text = ""

        self.folder_entry.configure(state="normal")
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, display_text)
        self.folder_entry.configure(state="readonly")
        logger.debug(f"Folder entry updated: {display_text}")

    def _create_unlock_button(self):
        """Creates the unlock PDFs button."""
        logger.debug("Creating unlock button")
        self.unlock_button = create_button(
            self,
            text="Unlock PDFs",
            command=self._on_unlock_pdfs_clicked,
            width=BUTTON_WIDTH
        )
        self.unlock_button.pack(pady=(20, 10))
        logger.debug("Unlock button created successfully")

    def _on_unlock_pdfs_clicked(self):
        """Handle PDF unlock operation with proper error handling."""
        if not self.selected_folder:
            logger.warning("No folder selected for PDF unlock")
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        try:
            logger.info("Starting PDF unlock operation")
            unlock_pdfs_in_folder(self.selected_folder, parent_window=self)
            logger.info("PDF unlock operation completed successfully")
        except Exception as e:
            logger.error(f"PDF unlock operation failed: {str(e)}", exc_info=True)
            messagebox.showerror("Unlock Error", str(e))

    def _open_folder_in_explorer(self):
        """Open the current folder in the system's file explorer."""
        if self.selected_folder:
            try:
                from ...utils import open_in_file_explorer
                open_in_file_explorer(self.selected_folder)
                logger.debug(f"Opened folder in explorer: {self.selected_folder}")
            except Exception as e:
                logger.error(f"Failed to open folder in explorer: {str(e)}", exc_info=True)
                messagebox.showerror("Error", f"Failed to open folder: {str(e)}")

    def _destroy_folder_header(self):
        """Clean up folder header components."""
        logger.debug("Destroying folder header")
        if self.folder_header_frame:
            self.folder_header_frame.pack_forget()
            self.folder_header_frame.destroy()
            self.folder_header_frame = None

        self.folder_copy_button = None
        self.folder_entry = None

    def destroy_frame(self):
        """Clean up all components when destroying the frame."""
        logger.info("Destroying PDFUnlockFrame")
        self._destroy_folder_header()
        if self.unlock_button:
            self.unlock_button.destroy()
            self.unlock_button = None
        if self.select_folder_button:
            self.select_folder_button.destroy()
            self.select_folder_button = None
        logger.info("PDFUnlockFrame destroyed successfully") 