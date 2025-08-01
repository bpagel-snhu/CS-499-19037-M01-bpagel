import customtkinter as ctk
from tkinter import messagebox
from typing import List, Tuple, Optional

from ...constants import (
    FRAME_PADDING, GRID_PADDING, GRID_ROW_PADDING,
    FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_LARGE,
    TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR
)
from ...ui_utils import create_button
from ...logging_config import ui_logger as logger
from .database_manager import DatabaseManager
from .dialogs import AddClientDialog, EditClientDialog


class DatabaseFrame(ctk.CTkFrame):
    """
    Database tool frame for managing client information and bank statement tracking.
    """

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.db_manager = DatabaseManager()
        
        # Initialize variables
        self.clients = []
        self.selected_client_id = None
        self.show_archived_var = ctk.BooleanVar(value=False)
        
        self._create_widgets()
        self._load_clients()



    def _create_widgets(self):
        """Create all UI widgets for the database frame."""
        logger.debug("Creating database frame widgets")

        # Main content frame
        self.inner_frame = ctk.CTkFrame(self, fg_color=TRANSPARENT_COLOR)
        self.inner_frame.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

        # Create the client selection row using a dedicated function
        self._create_client_selection_row()

        # Placeholder for future functionality
        self._create_placeholder_section()

    def _create_client_selection_row(self):
        """Create the client selection row with proper layout following settings frame pattern."""
        # Client selection row frame
        row_frame = ctk.CTkFrame(self.inner_frame, fg_color=TRANSPARENT_COLOR)
        row_frame.pack(fill="x", padx=FRAME_PADDING, pady=(10, 5))

        # Header label (fixed width)
        header_label = ctk.CTkLabel(
            row_frame, 
            text="Client:", 
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), 
            width=80, 
            anchor="w", 
            fg_color=TRANSPARENT_COLOR
        )
        header_label.pack(side="left", padx=(0, 5))

        # Container for the dropdown
        dropdown_container = ctk.CTkFrame(row_frame, fg_color=TRANSPARENT_COLOR)
        dropdown_container.pack(side="left", fill="x", expand=True)

        # Client dropdown with proper styling
        self.client_dropdown = ctk.CTkOptionMenu(
            dropdown_container,
            values=["Select client"],
            command=self._on_client_selected,
            width=300,
            height=35,
            fg_color=("gray70", "gray30"),
            button_color=("gray75", "gray25"),
            button_hover_color=HOVER_COLOR,
            dropdown_hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.client_dropdown.pack(side="left", fill="x", expand=True)

        # Show archived checkbox with word-wrapped text
        archived_frame = ctk.CTkFrame(row_frame, fg_color=TRANSPARENT_COLOR)
        archived_frame.pack(side="left", padx=(10, 0))
        
        # Checkbox without text
        self.show_archived_checkbox = ctk.CTkCheckBox(
            archived_frame,
            text="",  # No text on checkbox
            variable=self.show_archived_var,
            command=self._on_show_archived_changed,
            width=20
        )
        self.show_archived_checkbox.pack(side="left", padx=(0, 5))
        
        # Text label that wraps
        archived_text = ctk.CTkLabel(
            archived_frame,
            text="Show\nArchived",
            font=(FONT_FAMILY, 10),
            justify="left",
            anchor="w"
        )
        archived_text.pack(side="left")

        # Edit client button (initially disabled)
        self.edit_client_button = create_button(
            row_frame,
            text="Edit",
            command=self._on_edit_client,
            width=90
        )
        self.edit_client_button.pack(side="left", padx=(10, 0))
        self.edit_client_button.configure(state="disabled")

        # Add client button
        self.add_client_button = create_button(
            row_frame,
            text="Add New",
            command=self._on_add_client,
            width=90
        )
        self.add_client_button.pack(side="left", padx=(10, 0))

    def _create_placeholder_section(self):
        """Create placeholder section for future functionality."""
        placeholder_frame = ctk.CTkFrame(self.inner_frame, fg_color=TRANSPARENT_COLOR)
        placeholder_frame.pack(fill="both", expand=True, pady=(FRAME_PADDING, 0))

        placeholder_label = ctk.CTkLabel(
            placeholder_frame,
            text="Bank Statement Analysis\n(Coming Soon)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            justify="center"
        )
        placeholder_label.pack(expand=True)

    def _load_clients(self):
        """Load clients from database and update dropdown."""
        try:
            include_archived = self.show_archived_var.get()
            self.clients = self.db_manager.get_clients(include_archived=include_archived)
            
            if self.clients:
                dropdown_values = ["Select client"]
                for client_id, first_name, last_name, is_active in self.clients:
                    status = " (Archived)" if not is_active else ""
                    dropdown_values.append(f"{last_name}, {first_name}{status}")
                
                self.client_dropdown.configure(values=dropdown_values)
                self.client_dropdown.set("Select client")
                self.selected_client_id = None
            else:
                self.client_dropdown.configure(values=["Select client"])
                self.client_dropdown.set("Select client")
                self.selected_client_id = None
                
        except Exception as e:
            logger.error(f"Failed to load clients: {e}")
            messagebox.showerror("Database Error", f"Failed to load clients: {e}")

    def _load_clients_and_reselect_by_id(self, client_id_to_select: int):
        """Load clients from database and reselect a specific client by ID."""
        try:
            include_archived = self.show_archived_var.get()
            self.clients = self.db_manager.get_clients(include_archived=include_archived)
            
            if self.clients:
                dropdown_values = ["Select client"]
                client_found = False
                
                for client_id, first_name, last_name, is_active in self.clients:
                    status = " (Archived)" if not is_active else ""
                    dropdown_value = f"{last_name}, {first_name}{status}"
                    dropdown_values.append(dropdown_value)
                    
                    # Check if this is the client we want to reselect
                    if client_id == client_id_to_select:
                        client_found = True
                        self.selected_client_id = client_id
                        self.edit_client_button.configure(state="normal")
                
                self.client_dropdown.configure(values=dropdown_values)
                
                if client_found:
                    # Find the dropdown value for this client and select it
                    for client_id, first_name, last_name, is_active in self.clients:
                        if client_id == client_id_to_select:
                            status = " (Archived)" if not is_active else ""
                            dropdown_value = f"{last_name}, {first_name}{status}"
                            self.client_dropdown.set(dropdown_value)
                            break
                else:
                    # If client not found (e.g., was deleted), reset selection
                    self.client_dropdown.set("Select client")
                    self.selected_client_id = None
                    self.edit_client_button.configure(state="disabled")
            else:
                self.client_dropdown.configure(values=["Select client"])
                self.client_dropdown.set("Select client")
                self.selected_client_id = None
                self.edit_client_button.configure(state="disabled")
                
        except Exception as e:
            logger.error(f"Failed to load clients: {e}")
            messagebox.showerror("Database Error", f"Failed to load clients: {e}")

    def _on_show_archived_changed(self):
        """Handle show archived checkbox change."""
        self._load_clients()

    def _on_client_selected(self, selection):
        """Handle client dropdown selection."""
        if selection == "Select client":
            self.selected_client_id = None
            self.edit_client_button.configure(state="disabled")
        elif self.clients:
            # Find the selected client
            for client_id, first_name, last_name, is_active in self.clients:
                status = " (Archived)" if not is_active else ""
                if f"{last_name}, {first_name}{status}" == selection:
                    self.selected_client_id = client_id
                    self.edit_client_button.configure(state="normal")
                    logger.debug(f"Selected client: {first_name} {last_name} (ID: {client_id})")
                    break

    def _on_add_client(self):
        """Open add client dialog."""
        self._show_add_client_dialog()

    def _on_edit_client(self):
        """Open edit client dialog."""
        if self.selected_client_id is not None:
            self._show_edit_client_dialog()

    def _show_add_client_dialog(self):
        """Show dialog to add a new client."""
        dialog = AddClientDialog(self, self.db_manager)
        self.wait_window(dialog)
        if dialog.result:
            self._load_clients()
            # Show success toast
            self.main_window.show_toast("Client added successfully!")

    def _show_edit_client_dialog(self):
        """Show dialog to edit the selected client."""
        if self.selected_client_id is not None:
            # Get the current client data
            client_data = self.db_manager.get_client_by_id(self.selected_client_id)
            if client_data:
                # Store the client ID for reselection after update
                client_id_to_reselect = self.selected_client_id
                
                dialog = EditClientDialog(self, self.db_manager, client_data)
                self.wait_window(dialog)
                if dialog.result:
                    if dialog.result == "deleted":
                        # Client was deleted, reset selection
                        self.selected_client_id = None
                        self.client_dropdown.set("Select client")
                        self.edit_client_button.configure(state="disabled")
                        # Show deletion toast
                        self.main_window.show_toast("Client deleted successfully!")
                    else:
                        # Client was updated - keep it selected
                        self.main_window.show_toast("Client updated successfully!")
                        # Reload clients and reselect the updated client by ID
                        self._load_clients_and_reselect_by_id(client_id_to_reselect)
                        return  # Don't call _load_clients() again
                    self._load_clients() 