"""
Edit Client Dialog

This module contains the dialog for editing existing clients in the database.
"""

import customtkinter as ctk
from tkinter import messagebox

from ....constants import (
    FRAME_PADDING, GRID_PADDING,
    FONT_FAMILY, FONT_SIZE_NORMAL,
    TRANSPARENT_COLOR, HOVER_COLOR
)
from ....ui_utils import create_button, create_inline_form_field, create_standard_switch_field, create_inline_label_field, create_standard_ui_row
from ....logging_config import ui_logger as logger


class EditClientDialog(ctk.CTkToplevel):
    """Dialog for editing an existing client."""

    def __init__(self, parent, db_manager, client_data):
        super().__init__(parent)
        self.db_manager = db_manager
        self.client_data = client_data  # (id, first_name, last_name, is_active, created_date, updated_date)
        self.result = None
        
        # Dialog dimensions
        DIALOG_WIDTH = 400
        DIALOG_HEIGHT = 450
        
        # Configure dialog
        self.title("Edit Client")
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
            label_text="First Name:",
            initial_value=self.client_data[1]  # first_name
        )

        # Last name field (inline)
        self.last_name_label, self.last_name_entry = create_inline_form_field(
            parent=form_frame,
            label_text="Last Name:",
            initial_value=self.client_data[2]  # last_name
        )

        # Created date display (as label)
        created_value = ""
        if len(self.client_data) > 4 and self.client_data[4]:  # created_date
            created_value = self.db_manager.format_timestamp(self.client_data[4])
        
        self.created_label, self.created_display = create_inline_label_field(
            parent=form_frame,
            label_text="Created:",
            value_text=created_value
        )

        # Updated date display (as label)
        updated_value = ""
        if len(self.client_data) > 5 and self.client_data[5]:  # updated_date
            updated_value = self.db_manager.format_timestamp(self.client_data[5])
        
        self.updated_label, self.updated_display = create_inline_label_field(
            parent=form_frame,
            label_text="Last Updated:",
            value_text=updated_value
        )

        # Archived status switch field (at bottom)
        self.archived_label, self.is_archived_switch, self.is_archived_var = create_standard_switch_field(
            parent=form_frame,
            label_text="Archive Client:",
            initial_value=not self.client_data[3]  # Invert is_active to get is_archived
        )

        # Delete button field (following the same pattern as other form fields)
        delete_field_frame = ctk.CTkFrame(form_frame, fg_color=TRANSPARENT_COLOR)
        delete_field_frame.pack(fill="x", pady=(0, 20))

        # Label on the left
        delete_label = ctk.CTkLabel(
            delete_field_frame,
            text="Permanently remove from database:",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            width=100,
            anchor="w"
        )
        delete_label.pack(side="left", padx=(0, 10))

        # Delete button on the right
        delete_button = create_button(
            delete_field_frame,
            text="Delete Client",
            command=self._on_delete,
            width=120,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        delete_button.pack(side="right")

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
            command=self._on_save,
            width=100
        )
        save_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # Status label (bottom center) - following app pattern
        status_label = ctk.CTkLabel(
            self,
            text="Edit Client",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            fg_color=("gray20", "gray20"),
            text_color=("gray70", "gray70"),
            corner_radius=5,
            width=150,
            height=30
        )
        status_label.place(relx=0.5, rely=1.0, anchor="s", x=0, y=-10)

        # Focus on first name entry
        self.first_name_entry.focus()

    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.destroy()

    def _on_save(self):
        """Handle save button."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        is_archived = self.is_archived_var.get()
        is_active = not is_archived  # Convert archived status to active status

        try:
            success = self.db_manager.update_client(
                self.client_data[0],  # client_id
                first_name,
                last_name,
                is_active
            )
            if success:
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Update Error", "Failed to update client. Client may not exist.")
                
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            logger.error(f"Failed to update client: {e}")
            messagebox.showerror("Database Error", f"Failed to update client: {e}")

    def _on_delete(self):
        """Handle delete button."""
        # Show confirmation dialog
        client_name = f"{self.client_data[1]} {self.client_data[2]}"
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the client '{client_name}'?\n\n"
            "This action cannot be undone and will permanently remove all associated data."
        )
        
        if result:
            try:
                success = self.db_manager.delete_client(self.client_data[0])  # client_id
                if success:
                    self.result = "deleted"  # Special result to indicate deletion
                    self.destroy()
                else:
                    messagebox.showerror("Delete Error", "Failed to delete client. Client may not exist.")
                    
            except Exception as e:
                logger.error(f"Failed to delete client: {e}")
                messagebox.showerror("Database Error", f"Failed to delete client: {e}") 