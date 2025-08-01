"""
Add Client Dialog

This module contains the dialog for adding new clients to the database.
"""

import customtkinter as ctk
from tkinter import messagebox

from ....constants import (
    FRAME_PADDING, FONT_FAMILY, 
    FONT_SIZE_NORMAL, TRANSPARENT_COLOR
)
from ....ui_utils import create_button, create_inline_form_field
from ....logging_config import ui_logger as logger


class AddClientDialog(ctk.CTkToplevel):
    """Dialog for adding a new client."""

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.result = None
        
        # Dialog dimensions
        DIALOG_WIDTH = 400
        DIALOG_HEIGHT = 200
        
        # Configure dialog
        self.title("Add New Client")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (DIALOG_WIDTH // 2)
        y = (self.winfo_screenheight() // 2) - (DIALOG_HEIGHT // 2)
        self.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}+{x}+{y}")
        
        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets following the application's consistent pattern."""
        # Main content frame
        main_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT_COLOR)
        main_frame.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

        # Form frame
        form_frame = ctk.CTkFrame(main_frame, fg_color=TRANSPARENT_COLOR)
        form_frame.pack(fill="both", expand=True, pady=(0, 50))  # Leave space for bottom elements

        # First name field (inline)
        self.first_name_label, self.first_name_entry = create_inline_form_field(
            parent=form_frame,
            label_text="First Name:"
        )

        # Last name field (inline)
        self.last_name_label, self.last_name_entry = create_inline_form_field(
            parent=form_frame,
            label_text="Last Name:"
        )

        # Back button (bottom left) - following app pattern
        back_button = create_button(
            self,
            text="← Back",
            command=self._on_cancel,
            width=100,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            text_color=("gray50", "gray50")
        )
        back_button.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

        # Save button (bottom right) - following app pattern
        save_button = create_button(
            self,
            text="Save",
            command=self._on_add,
            width=100
        )
        save_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # Status label (bottom center) - following app pattern
        status_label = ctk.CTkLabel(
            self,
            text="Add New Client",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            fg_color=("gray20", "gray20"),
            text_color=("gray70", "gray70"),
            corner_radius=5,
            width=150,
            height=30
        )
        status_label.place(relx=0.5, rely=1.0, anchor="s", x=0, y=-10)

        # Bind Enter key to save
        self.first_name_entry.bind("<Return>", lambda event: self._on_add())
        self.last_name_entry.bind("<Return>", lambda event: self._on_add())
        
        # Schedule focus after dialog is fully created
        self.after(100, self.first_name_entry.focus)

    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.destroy()

    def _on_add(self):
        """Handle add button."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        # New clients are assumed to be active
        is_active = True

        try:
            self.db_manager.add_client(first_name, last_name, is_active)
            self.result = True
            self.destroy()
                
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            logger.error(f"Failed to add client: {e}")
            messagebox.showerror("Database Error", f"Failed to add client: {e}") 