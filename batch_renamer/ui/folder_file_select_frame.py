# batch_renamer/ui/folder_file_select_frame.py

import customtkinter as ctk
from tkinter import filedialog
import os

# Import the interactive backup function
from batch_renamer.backup_logic import create_backup_interactive

# Import rename options frame (assuming it's in the same package)
from .rename_options_frame import RenameOptionsFrame


class FolderFileSelectFrame(ctk.CTkFrame):
    """
    Combined frame that handles BOTH the folder row and file row in a unified style.
    Calls 'create_backup_interactive' when creating a backup.
    Displays rename options once a file is selected or changed.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.select_folder_button = None
        self.folder_header_frame = None
        self.folder_prefix_button = None
        self.folder_copy_button = None
        self.folder_entry = None
        self.create_backup_button = None
        self.change_folder_button = None

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

    # ─────────────────────────────────────────────
    # SELECT FOLDER
    # ─────────────────────────────────────────────
    def _create_select_folder_button(self):
        """Creates the 'Select Folder' button with padding."""
        self.select_folder_button = ctk.CTkButton(
            self,
            text="Select Target Folder",
            command=self._on_select_folder
        )
        self.select_folder_button.pack(padx=20, pady=(20, 20))

    def _on_select_folder(self):
        """After user picks a folder, show folder header & 'Select Sample File' button."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.parent.full_folder_path = folder_selected
            self.parent.folder_name = os.path.basename(folder_selected)
            self.parent.show_full_path = False

            # Hide 'Select Folder' button
            self.select_folder_button.pack_forget()

            # Create folder header row
            self._create_folder_header()
            # Show 'Select Sample File' button
            self._create_select_file_button()

    def _create_folder_header(self):
        """Displays folder info, 'Create Backup', and 'Change Folder' in one row."""
        self._destroy_folder_header()

        self.folder_header_frame = ctk.CTkFrame(self)
        self.folder_header_frame.pack(fill="x", padx=20, pady=(10, 10))

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

    def _toggle_folder_path(self):
        self.parent.show_full_path = not self.parent.show_full_path
        self._update_folder_entry()

    def _update_folder_entry(self):
        if not self.parent.full_folder_path or not self.parent.folder_name:
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

    def _copy_folder_to_clipboard(self):
        if not self.parent.full_folder_path or not self.parent.folder_name:
            return
        text = (
            self.parent.full_folder_path
            if self.parent.show_full_path
            else self.parent.folder_name
        )
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.show_toast("Copied folder to clipboard!")

    def _on_change_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.parent.full_folder_path = folder_selected
            self.parent.folder_name = os.path.basename(folder_selected)
            self.parent.show_full_path = False
            self._update_folder_entry()

            # Destroy file row if present
            self._destroy_file_header()
            if self.select_file_button:
                self.select_file_button.pack_forget()
                self.select_file_button = None

            # Destroy rename options if displayed
            if self.rename_options_frame:
                self.rename_options_frame.destroy()
                self.rename_options_frame = None

            self.parent.full_file_path = None
            self.parent.file_name = None
            self.parent.show_full_file_path = False

    def _on_create_backup_clicked(self):
        """Calls the interactive backup function from backup_logic."""
        create_backup_interactive(self.parent.full_folder_path)

    def _destroy_folder_header(self):
        if self.folder_header_frame:
            self.folder_header_frame.pack_forget()
            self.folder_header_frame.destroy()
            self.folder_header_frame = None

        self.folder_prefix_button = None
        self.folder_copy_button = None
        self.folder_entry = None
        self.create_backup_button = None
        self.change_folder_button = None

    # ─────────────────────────────────────────────
    # FILE SELECTION
    # ─────────────────────────────────────────────
    def _create_select_file_button(self):
        """Creates "Select Sample File" button with padding."""
        self.select_file_button = ctk.CTkButton(
            self,
            text="Select Sample File",
            command=self._on_select_sample_file
        )
        self.select_file_button.pack(padx=20, pady=(0, 10))

    def _on_select_sample_file(self):
        if not self.parent.full_folder_path:
            return
        file_selected = filedialog.askopenfilename(initialdir=self.parent.full_folder_path)
        if file_selected:
            self.parent.full_file_path = file_selected
            self.parent.file_name = os.path.basename(file_selected)
            self.parent.show_full_file_path = False

            self.select_file_button.pack_forget()
            self._create_file_header()

            # Show rename options
            self._create_rename_options_frame()

    def _create_file_header(self):
        """Creates the row for toggling/copying the sample file path."""
        self._destroy_file_header()

        self.file_header_frame = ctk.CTkFrame(self)
        self.file_header_frame.pack(fill="x", padx=20, pady=(10, 10))

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

        self._update_file_entry()

        self.change_file_button = ctk.CTkButton(
            self.file_header_frame,
            text="Change Example File",
            command=self._on_change_file
        )
        self.change_file_button.pack(side="right", padx=(10, 0))

    def _toggle_file_path(self):
        self.parent.show_full_file_path = not self.parent.show_full_file_path
        self._update_file_entry()

    def _copy_file_to_clipboard(self):
        if not self.parent.full_file_path or not self.parent.file_name:
            return
        text = (
            self.parent.full_file_path
            if self.parent.show_full_file_path
            else self.parent.file_name
        )
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.show_toast("Copied file to clipboard!")

    def _update_file_entry(self):
        if not self.parent.full_file_path or not self.parent.file_name:
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

    def _on_change_file(self):
        """User changes the sample file again. We'll reset the rename options, too."""
        if not self.parent.full_folder_path:
            return
        file_selected = filedialog.askopenfilename(initialdir=self.parent.full_folder_path)
        if file_selected:
            self.parent.full_file_path = file_selected
            self.parent.file_name = os.path.basename(file_selected)
            self.parent.show_full_file_path = False
            self._update_file_entry()

            # Because the file changed, let's refresh rename options
            if self.rename_options_frame:
                self.rename_options_frame.destroy()
                self.rename_options_frame = None

            self._create_rename_options_frame()

    def _destroy_file_header(self):
        if self.file_header_frame:
            self.file_header_frame.pack_forget()
            self.file_header_frame.destroy()
            self.file_header_frame = None

        self.file_prefix_button = None
        self.file_copy_button = None
        self.file_entry = None
        self.change_file_button = None

    # ─────────────────────────────────────────────
    # RENAME OPTIONS
    # ─────────────────────────────────────────────
    def _create_rename_options_frame(self):
        """Destroy any existing rename frame and recreate it for the newly selected file."""
        if self.rename_options_frame:
            self.rename_options_frame.destroy()

        # Re-instantiate the rename options with the new file
        from .rename_options_frame import RenameOptionsFrame
        self.rename_options_frame = RenameOptionsFrame(self.parent)
        self.rename_options_frame.pack(fill="x", padx=20, pady=(0, 20))

    # ─────────────────────────────────────────────
    # DESTROY FRAME
    # ─────────────────────────────────────────────
    def destroy_frame(self):
        """If the main window or logic resets this entire frame."""
        if self.select_folder_button:
            self.select_folder_button.pack_forget()
            self.select_folder_button = None

        if self.select_file_button:
            self.select_file_button.pack_forget()
            self.select_file_button = None

        if self.rename_options_frame:
            self.rename_options_frame.destroy()
            self.rename_options_frame = None

        self._destroy_folder_header()
        self._destroy_file_header()
        self.destroy()
