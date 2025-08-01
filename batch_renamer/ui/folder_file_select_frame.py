# batch_renamer/ui/folder_file_select_frame.py

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from ..logging_config import ui_logger as logger
from ..constants import (
    FRAME_PADDING, GRID_PADDING, GRID_ROW_PADDING, TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR,
    SELECT_FOLDER_TEXT, SELECT_FILE_TEXT, CHANGE_FOLDER_TEXT, CHANGE_FILE_TEXT,
    CREATE_BACKUP_TEXT
)
from ..ui_utils import create_button
from ..utils import copy_to_clipboard

from batch_renamer.backup_logic import create_backup_interactive
from ..exceptions import FileOperationError, ValidationError
from ..folder_file_logic import FolderFileManager


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

        # Use the manager from the main window
        self.manager = parent.manager

        # UI Components
        self.select_folder_button = None
        self.folder_header_frame = None
        self.folder_prefix_button = None
        self.folder_copy_button = None
        self.folder_entry = None
        self.create_backup_button = None
        self.change_folder_button = None

        self.file_buttons_frame = None
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
        self.select_folder_button = create_button(
            self,
            text=SELECT_FOLDER_TEXT,
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

            # Clear options container if it exists
            if hasattr(self, 'options_container') and self.options_container:
                logger.debug("Clearing existing options container")
                self.options_container.destroy()
                self.options_container = None

            # Update folder state using manager
            self.manager.clear_file()
            self.manager.set_folder(folder_selected)

            # Hide 'Select Folder' button
            self.select_folder_button.pack_forget()

            # Create folder UI
            self._create_folder_header()
            self._create_select_file_button()
            
            # Force layout update to ensure proper positioning
            self.update_idletasks()
            logger.info("Folder selection UI updated")



    def _create_folder_header(self):
        """Displays folder info, 'Create Backup', and 'Change Folder' in one row."""
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
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(GRID_PADDING, 0))

        # Right side: Create Backup + Change Folder
        self.change_folder_button = create_button(
            self.folder_header_frame,
            text=CHANGE_FOLDER_TEXT,
            command=self._on_change_folder
        )
        self.change_folder_button.pack(side="right", padx=(GRID_PADDING, 0))

        self.create_backup_button = create_button(
            self.folder_header_frame,
            text=CREATE_BACKUP_TEXT,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._on_create_backup_clicked
        )
        self.create_backup_button.pack(side="right", padx=(GRID_PADDING, 0))

        self._update_folder_entry()
        logger.debug("Folder header created successfully")

    def _toggle_folder_path(self):
        """Toggle between full and relative folder path display."""
        logger.debug("Toggling folder path display")
        self.manager.toggle_folder_path_display()
        self._update_folder_entry()

    def _update_folder_entry(self):
        """Update the folder entry display text."""
        display_text = self.manager.get_folder_display_path()
        self.folder_entry.configure(state="normal")
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, display_text)
        self.folder_entry.configure(state="readonly")
        logger.debug(f"Folder entry updated: {display_text}")

    def _copy_folder_to_clipboard(self):
        """Copy the current folder path to clipboard."""
        text = self.manager.get_folder_display_path()
        if text:
            copy_to_clipboard(text, self.parent)

    def _on_change_folder(self):
        """Handle folder change request."""
        logger.info("Initiating folder change")
        self._on_select_folder()

    def _on_create_backup_clicked(self):
        """Handle backup creation request."""
        try:
            logger.info("Initiating backup creation")
            create_backup_interactive(self.manager.full_folder_path)
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

        self.folder_copy_button = None
        self.folder_entry = None
        self.create_backup_button = None
        self.change_folder_button = None

    def _create_select_file_button(self):
        """Creates 'Select Sample File' button."""
        logger.debug("Creating file selection button")
        self.file_buttons_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT_COLOR)
        self.file_buttons_frame.pack(fill="x", pady=(0, 10))

        # Create a container frame to center the button
        button_container = ctk.CTkFrame(self.file_buttons_frame, fg_color=TRANSPARENT_COLOR)
        button_container.pack(expand=True)

        self.select_file_button = create_button(
            button_container,
            text=SELECT_FILE_TEXT,
            command=self._on_select_sample_file,
            width=180
        )
        self.select_file_button.pack()
        logger.debug("File selection button created successfully")

    def _on_select_sample_file(self):
        """Handle sample file selection."""
        if not self.manager.full_folder_path:
            logger.warning("Cannot select file: no folder selected")
            return
        logger.info("Opening file selection dialog")
        file_selected = filedialog.askopenfilename(initialdir=self.manager.full_folder_path)
        if file_selected:
            logger.info(f"File selected: {file_selected}")

            # Check filename length (without extension)
            base_name = os.path.splitext(os.path.basename(file_selected))[0]
            if len(base_name) < 6:
                from tkinter import messagebox
                messagebox.showerror(
                    "Invalid Sample Filename",
                    "Sample filename must include at least year and month (6 characters). Please select a different file."
                )
                return

            # Update file state using manager
            self.manager.set_file(file_selected)

            if self.file_buttons_frame:
                logger.debug("Clearing existing file buttons frame")
                self.file_buttons_frame.pack_forget()
                self.file_buttons_frame.destroy()
                self.file_buttons_frame = None

            logger.debug("Creating file header")
            self._create_file_header()

            # Destroy old RenameOptionsFrame and its container if they exist
            if hasattr(self, 'options_container') and self.options_container:
                self.options_container.destroy()
                self.options_container = None
            if self.rename_options_frame:
                self.rename_options_frame.destroy()
                self.rename_options_frame = None

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

        self.file_entry = ctk.CTkEntry(file_text_frame, state="readonly")
        self.file_entry.pack(side="left", fill="x", expand=True)

        self.change_file_button = create_button(
            self.file_header_frame,
            text=CHANGE_FILE_TEXT,
            command=self._on_change_file
        )
        self.change_file_button.pack(side="right", padx=(GRID_PADDING, 0))

        self._update_file_entry()
        logger.debug("File header created successfully")

    def _toggle_file_path(self):
        """Toggle between full and relative file path display."""
        logger.debug("Toggling file path display")
        self.manager.toggle_file_path_display()
        self._update_file_entry()

    def _update_file_entry(self):
        """Update the file entry display text."""
        display_text = self.manager.get_file_display_path()
        self.file_entry.configure(state="normal")
        self.file_entry.delete(0, "end")
        self.file_entry.insert(0, display_text)
        self.file_entry.configure(state="readonly")
        logger.debug(f"File entry updated: {display_text}")

    def _copy_file_to_clipboard(self):
        """Copy the current file path to clipboard."""
        text = self.manager.get_file_display_path()
        if text:
            copy_to_clipboard(text, self.parent)

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

        self.file_entry = None
        self.change_file_button = None

    def _create_rename_options_frame(self):
        """Create the frame for rename options."""
        logger.debug("Creating rename options frame")
        from ..tools.bulk_rename.rename_options_frame import RenameOptionsFrame

        # Create a container frame to ensure proper spacing
        self.options_container = ctk.CTkFrame(self, fg_color="transparent")
        self.options_container.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=(10, 10))

        self.rename_options_frame = RenameOptionsFrame(self.options_container, main_window=self.parent)
        self.rename_options_frame.pack(fill="both", expand=True)
        logger.debug("Rename options frame created successfully")

    def _open_folder_in_explorer(self):
        """Open the current folder in the system's file explorer."""
        if self.manager.full_folder_path:
            try:
                from ..utils import open_in_file_explorer
                open_in_file_explorer(self.manager.full_folder_path)
                logger.debug(f"Opened folder in explorer: {self.manager.full_folder_path}")
            except Exception as e:
                logger.error(f"Failed to open folder in explorer: {str(e)}", exc_info=True)
                messagebox.showerror("Error", f"Failed to open folder: {str(e)}")

    def destroy_frame(self):
        """Clean up all components when destroying the frame."""
        logger.info("Destroying FolderFileSelectFrame")
        self._destroy_folder_header()
        self._destroy_file_header()
        if self.rename_options_frame:
            self.rename_options_frame.destroy()
            self.rename_options_frame = None
        if hasattr(self, 'options_container') and self.options_container:
            self.options_container.destroy()
            self.options_container = None
        if self.file_buttons_frame:
            self.file_buttons_frame.destroy()
            self.file_buttons_frame = None
        if self.select_folder_button:
            self.select_folder_button.destroy()
            self.select_folder_button = None
        logger.info("FolderFileSelectFrame destroyed successfully")
