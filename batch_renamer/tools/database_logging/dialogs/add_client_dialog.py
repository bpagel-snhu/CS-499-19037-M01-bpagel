"""
Add Client Dialog

This module contains the dialog for adding new clients to the database.
"""

import customtkinter as ctk
from tkinter import messagebox

from ....constants import (
    FRAME_PADDING, GRID_PADDING,
    FONT_FAMILY, FONT_SIZE_NORMAL,
    TRANSPARENT_COLOR, HOVER_COLOR
)
from ....ui_utils import create_button, create_inline_form_field, create_standard_dialog_layout
from ....logging_config import ui_logger as logger


class AddClientDialog:
    """Dialog for adding a new client."""

    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.result = None
        
        # Use standard dialog layout
        self.dialog, self.content_frame, self.back_button, self.save_button, self.status_label = create_standard_dialog_layout(
            parent=parent,
            title="Add New Client",
            width=400,
            height=300
        )
        
        # Customize the save button command
        self.save_button.configure(command=self._on_add)
        
        # Customize the back button command
        self.back_button.configure(command=self._on_cancel)
        
        # Add dialog-specific content
        self._create_dialog_content()

    def _create_dialog_content(self):
        """Add dialog-specific content to the content frame."""
        # First name field (inline)
        self.first_name_label, self.first_name_entry = create_inline_form_field(
            parent=self.content_frame,
            label_text="First Name:"
        )

        # Last name field (inline)
        self.last_name_label, self.last_name_entry = create_inline_form_field(
            parent=self.content_frame,
            label_text="Last Name:"
        )

        # Focus on first name entry
        self.first_name_entry.focus()

    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.dialog.destroy()

    def _on_add(self):
        """Handle add button."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        # New clients are assumed to be active
        is_active = True

        try:
            self.db_manager.add_client(first_name, last_name, is_active)
            self.result = True
            self.dialog.destroy()
                
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            logger.error(f"Failed to add client: {e}")
            messagebox.showerror("Database Error", f"Failed to add client: {e}") 