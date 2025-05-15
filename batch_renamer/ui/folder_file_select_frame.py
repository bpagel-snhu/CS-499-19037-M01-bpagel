# batch_renamer/ui/folder_file_select_frame.py

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import pyperclip
from ..logging_config import ui_logger as logger
from ..constants import (
    FRAME_PADDING, BUTTON_WIDTH
)
from .pdf_unlock_helper import unlock_pdfs_in_folder

# Import the interactive backup function
from batch_renamer.backup_logic import create_backup_interactive
from ..exceptions import FileOperationError, ValidationError

class FolderFileSelectFrame(ctk.CTkFrame):
    """
    Combined frame that handles BOTH the folder row and file row in a unified style.
    Calls 'create_backup_interactive' when creating a backup.
    Displays rename options once a file is selected or changed.
    """

    def __init__(self, parent):
        super().__init__(parent)
        logger.info("Initializing FolderFileSelectFrame")
        self.parent = parent

        self.select_folder_button = None
        self.folder_header_frame = None
        self.folder_prefix_button = None
        self.folder_copy_button = None
        self.folder_entry = None
        self.create_backup_button = None
        self.change_folder_button = None

        self.file_buttons_frame = None
        self.unlock_pdfs_button = None
        self.select_file_button = None
        self.file_header_frame = None
        self.file_prefix_button = None
        self.file_copy_button = None
        self.file_entry = None
        self.change_file_button = None

        # Reference to the rename options frame
        self.rename_options_frame = None

        # Show the "Select Folder" button initially
        self._create_select_folder_button()
        logger.info("FolderFileSelectFrame initialization complete")

    def _create_select_folder_button(self):
        """Creates the 'Select Folder' button with padding."""
        logger.debug("Creating select folder button")
        self.select_folder_button = ctk.CTkButton(
            self,
            text="Select Target Folder",
            command=self._on_select_folder
        )
        self.select_folder_button.pack(padx=FRAME_PADDING, pady=(FRAME_PADDING, FRAME_PADDING))

    def _on_select_folder(self):
        """After user picks a folder, clear UI and show folder header & 'Select Sample File' button."""
        logger.info("Opening folder selection dialog")
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            logger.info(f"Folder selected: {folder_selected}")
            # Clear any existing UI elements before updating
            if self.file_buttons_frame:
                logger.debug("Clearing existing file buttons frame")
                self.file_buttons_frame.pack_forget()
                self.file_buttons_frame.destroy()
                self.file_buttons_frame = None

            if self.select_file_button:
                logger.debug("Clearing existing select file button")
                self.select_file_button.pack_forget()
                self.select_file_button = None

            self._destroy_file_header()

            if self.rename_options_frame:
                logger.debug("Clearing existing rename options frame")
                self.rename_options_frame.destroy()
                self.rename_options_frame = None

            self.parent.full_file_path = None
            self.parent.file_name = None
            self.parent.show_full_file_path = False

            # Update folder state
            self.parent.full_folder_path = folder_selected
            self.parent.folder_name = os.path.basename(folder_selected)
            self.parent.show_full_path = False

            # Hide 'Select Folder' button
            self.select_folder_button.pack_forget()

            # Create folder UI
            self._create_folder_header()
            self._create_select_file_button()
            logger.info("Folder selection UI updated")

    def _on_unlock_pdfs_clicked(self):
        """Handle PDF unlock operation with proper error handling."""
        try:
            logger.info("Starting PDF unlock operation")
            unlock_pdfs_in_folder(self.parent.full_folder_path, parent_window=self)
            logger.info("PDF unlock operation completed successfully")
        except Exception as e:
            logger.error(f"PDF unlock operation failed: {str(e)}", exc_info=True)
            messagebox.showerror("Unlock Error", str(e))

    def _create_folder_header(self):
        """Displays folder info, 'Create Backup', and 'Change Folder' in one row."""
        logger.debug("Creating folder header")
        self._destroy_folder_header()

        self.folder_header_frame = ctk.CTkFrame(self)
        self.folder_header_frame.pack(fill="x", padx=FRAME_PADDING, pady=(10, 10))

        folder_text_frame = ctk.CTkFrame(self.folder_header_frame)
        folder_text_frame.pack(side="left", fill="x", expand=True)

        self.folder_prefix_button = ctk.CTkButton(
            folder_text_frame,
            text="./",
            width=40,
            fg_color="transparent",
            hover_color="gray40",
            text_color="gray70",
            command=self._toggle_folder_path
        )
        self.folder_prefix_button.pack(side="left")

        self.folder_copy_button = ctk.CTkButton(
            folder_text_frame,
            text="^",
            width=30,
            fg_color="transparent",
            hover_color="gray40",
            text_color="gray70",
            command=self._copy_folder_to_clipboard
        )
        self.folder_copy_button.pack(side="left", padx=(5, 0))

        self.folder_entry = ctk.CTkEntry(folder_text_frame, state="readonly")
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Right side: Create Backup + Change Folder
        self.change_folder_button = ctk.CTkButton(
            self.folder_header_frame,
            text="Change Target Folder",
            command=self._on_change_folder
        )
        self.change_folder_button.pack(side="right", padx=(10, 0))

        self.create_backup_button = ctk.CTkButton(
            self.folder_header_frame,
            text="Create Backup",
            fg_color="transparent",
            hover_color="gray40",
            text_color="gray70",
            command=self._on_create_backup_clicked
        )
        self.create_backup_button.pack(side="right", padx=(10, 0))

        self._update_folder_entry()
        logger.debug("Folder header created successfully")

    def _toggle_folder_path(self):
        """Toggle between full and relative folder path display."""
        logger.debug("Toggling folder path display")
        self.parent.show_full_path = not self.parent.show_full_path
        self._update_folder_entry()

    def _update_folder_entry(self):
        """Update the folder entry display text."""
        if not self.parent.full_folder_path or not self.parent.folder_name:
            logger.warning("Cannot update folder entry: missing folder path or name")
            return
        display_text = (
            self.parent.full_folder_path
            if self.parent.show_full_path
            else self.parent.folder_name
        )
        self.folder_entry.configure(state="normal")
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, display_text)
        self.folder_entry.configure(state="readonly")
        logger.debug(f"Folder entry updated: {display_text}")

    def _copy_folder_to_clipboard(self):
        """Copy the current folder path to clipboard."""
        if not self.parent.full_folder_path or not self.parent.folder_name:
            logger.warning("Cannot copy to clipboard: missing folder path or name")
            return
        text = (
            self.parent.full_folder_path
            if self.parent.show_full_path
            else self.parent.folder_name
        )
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        logger.debug(f"Copied to clipboard: {text}")
        self.parent.show_toast("Copied folder to clipboard!")

    def _on_change_folder(self):
        """Handle folder change request."""
        logger.info("Initiating folder change")
        self._on_select_folder()

    def _on_create_backup_clicked(self):
        """Handle backup creation request."""
        try:
            logger.info("Initiating backup creation")
            create_backup_interactive(self.parent.full_folder_path)
            logger.info("Backup creation completed successfully")
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}", exc_info=True)
            messagebox.showerror("Backup Error", str(e))

    def _destroy_folder_header(self):
        """Clean up folder header components."""
        logger.debug("Destroying folder header")
        if self.folder_header_frame:
            self.folder_header_frame.pack_forget()
            self.folder_header_frame.destroy()
            self.folder_header_frame = None

        self.folder_prefix_button = None
        self.folder_copy_button = None
        self.folder_entry = None
        self.create_backup_button = None
        self.change_folder_button = None

    def _create_select_file_button(self):
        """Creates 'Select Sample File' and 'Unlock PDFs' buttons side-by-side."""
        logger.debug("Creating file selection buttons")
        self.file_buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_buttons_frame.pack(fill="x", pady=(0, 10))

        # Create a container frame to center the buttons
        button_container = ctk.CTkFrame(self.file_buttons_frame, fg_color="transparent")
        button_container.pack(expand=True)

        self.select_file_button = ctk.CTkButton(
            button_container,
            text="Select Sample File",
            command=self._on_select_sample_file,
            width=BUTTON_WIDTH
        )
        self.select_file_button.pack(side="left", padx=(0, 10))

        self.unlock_pdfs_button = ctk.CTkButton(
            button_container,
            text="Unlock PDFs",
            command=self._on_unlock_pdfs_clicked,
            width=BUTTON_WIDTH
        )
        self.unlock_pdfs_button.pack(side="left")
        logger.debug("File selection buttons created successfully")

    def _on_select_sample_file(self):
        """Handle sample file selection."""
        if not self.parent.full_folder_path:
            logger.warning("Cannot select file: no folder selected")
            return
        logger.info("Opening file selection dialog")
        file_selected = filedialog.askopenfilename(initialdir=self.parent.full_folder_path)
        if file_selected:
            logger.info(f"File selected: {file_selected}")
            self.parent.full_file_path = file_selected
            self.parent.file_name = os.path.basename(file_selected)
            self.parent.show_full_file_path = False
            logger.debug(f"Parent state updated - file_name: {self.parent.file_name}, full_file_path: {self.parent.full_file_path}")

            if self.file_buttons_frame:
                logger.debug("Clearing existing file buttons frame")
                self.file_buttons_frame.pack_forget()
                self.file_buttons_frame.destroy()
                self.file_buttons_frame = None

            logger.debug("Creating file header")
            self._create_file_header()

            logger.debug("Creating rename options frame")
            self._create_rename_options_frame()
            
            if self.rename_options_frame:
                logger.info("Rename options frame created and packed successfully")
            else:
                logger.error("Failed to create rename options frame")
            
            logger.info("File selection UI updated")

    def _create_file_header(self):
        """Creates the row for toggling/copying the sample file path."""
        logger.debug("Creating file header")
        self._destroy_file_header()

        self.file_header_frame = ctk.CTkFrame(self)
        self.file_header_frame.pack(fill="x", padx=FRAME_PADDING, pady=(10, 10))

        file_text_frame = ctk.CTkFrame(self.file_header_frame)
        file_text_frame.pack(side="left", fill="x", expand=True)

        self.file_prefix_button = ctk.CTkButton(
            file_text_frame,
            text="./",
            width=40,
            fg_color="transparent",
            hover_color="gray40",
            text_color="gray70",
            command=self._toggle_file_path
        )
        self.file_prefix_button.pack(side="left")

        self.file_copy_button = ctk.CTkButton(
            file_text_frame,
            text="^",
            width=30,
            fg_color="transparent",
            hover_color="gray40",
            text_color="gray70",
            command=self._copy_file_to_clipboard
        )
        self.file_copy_button.pack(side="left", padx=(5, 0))

        self.file_entry = ctk.CTkEntry(file_text_frame, state="readonly")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.change_file_button = ctk.CTkButton(
            self.file_header_frame,
            text="Change Sample File",
            command=self._on_change_file
        )
        self.change_file_button.pack(side="right", padx=(10, 0))

        self._update_file_entry()
        logger.debug("File header created successfully")

    def _toggle_file_path(self):
        """Toggle between full and relative file path display."""
        logger.debug("Toggling file path display")
        self.parent.show_full_file_path = not self.parent.show_full_file_path
        self._update_file_entry()

    def _copy_file_to_clipboard(self):
        """Copy the current file path to clipboard."""
        if not self.parent.full_file_path or not self.parent.file_name:
            logger.warning("Cannot copy to clipboard: missing file path or name")
            return
        text = (
            self.parent.full_file_path
            if self.parent.show_full_file_path
            else self.parent.file_name
        )
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        logger.debug(f"Copied to clipboard: {text}")
        self.parent.show_toast("Copied file to clipboard!")

    def _update_file_entry(self):
        """Update the file entry display text."""
        if not self.parent.full_file_path or not self.parent.file_name:
            logger.warning("Cannot update file entry: missing file path or name")
            return
        display_text = (
            self.parent.full_file_path
            if self.parent.show_full_file_path
            else self.parent.file_name
        )
        self.file_entry.configure(state="normal")
        self.file_entry.delete(0, "end")
        self.file_entry.insert(0, display_text)
        self.file_entry.configure(state="readonly")
        logger.debug(f"File entry updated: {display_text}")

    def _on_change_file(self):
        """Handle file change request."""
        logger.info("Initiating file change")
        self._on_select_sample_file()

    def _destroy_file_header(self):
        """Clean up file header components."""
        logger.debug("Destroying file header")
        if self.file_header_frame:
            self.file_header_frame.pack_forget()
            self.file_header_frame.destroy()
            self.file_header_frame = None

        self.file_prefix_button = None
        self.file_copy_button = None
        self.file_entry = None
        self.change_file_button = None

    def _create_rename_options_frame(self):
        """Create the frame for rename options."""
        logger.debug("Creating rename options frame")
        from .rename_options_frame import RenameOptionsFrame
        
        # Create a container frame to ensure proper spacing
        options_container = ctk.CTkFrame(self, fg_color="transparent")
        options_container.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=(10, 10))
        
        self.rename_options_frame = RenameOptionsFrame(options_container, main_window=self.parent)
        self.rename_options_frame.pack(fill="both", expand=True)
        logger.debug("Rename options frame created successfully")

    def destroy_frame(self):
        """Clean up all components when destroying the frame."""
        logger.info("Destroying FolderFileSelectFrame")
        self._destroy_folder_header()
        self._destroy_file_header()
        if self.rename_options_frame:
            self.rename_options_frame.destroy()
            self.rename_options_frame = None
        if self.file_buttons_frame:
            self.file_buttons_frame.destroy()
            self.file_buttons_frame = None
        if self.select_folder_button:
            self.select_folder_button.destroy()
            self.select_folder_button = None
        logger.info("FolderFileSelectFrame destroyed successfully") 