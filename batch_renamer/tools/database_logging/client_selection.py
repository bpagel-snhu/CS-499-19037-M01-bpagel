import customtkinter as ctk
import logging
from typing import List, Tuple, Optional
from tkinter import messagebox
from .database_manager import DatabaseManager
from ...constants import (
    FONT_FAMILY, FONT_SIZE_NORMAL,
    TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR
)
from ...ui_utils import create_button

logger = logging.getLogger(__name__)

# Local padding constant for this component
PADDING = 2


class ClientSelection:
    """Manages client selection dropdown and related functionality."""
    
    def __init__(self, parent_frame, db_manager: DatabaseManager, main_window):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.main_window = main_window
        self.clients = []
        self.selected_client_id = None
        self.show_archived_var = ctk.BooleanVar(value=False)
        
        # UI elements
        self.row_frame = None # Initialized to None
        self.client_dropdown = None
        self.edit_client_button = None
        self.add_client_button = None
        self.show_archived_checkbox = None
        
    def create_client_selection_row(self):
        """Create the client selection row with proper layout."""
        # Client selection row frame
        self.row_frame = ctk.CTkFrame(self.parent_frame, fg_color=TRANSPARENT_COLOR)
        # Don't pack it yet - it will be shown by the parent frame
        
        # Client dropdown container (left side, expandable)
        dropdown_container = ctk.CTkFrame(self.row_frame, fg_color=TRANSPARENT_COLOR)
        dropdown_container.pack(side="left", fill="x", expand=True, padx=PADDING, pady=PADDING)
        dropdown_container.pack_propagate(True)
        
        # Client dropdown
        self.client_dropdown = ctk.CTkComboBox(
            dropdown_container,
            values=["Select client"],
            state="readonly",
            width=0  # Let it expand to fill the container
        )
        self.client_dropdown.pack(fill="x", expand=True)
        
        # Buttons container (right side, fixed width)
        buttons_container = ctk.CTkFrame(self.row_frame, fg_color=TRANSPARENT_COLOR)
        buttons_container.pack(side="right", padx=PADDING, pady=PADDING)
        
        # Add client button
        self.add_client_button = ctk.CTkButton(
            buttons_container,
            text="Add",
            width=60,
            height=30
        )
        self.add_client_button.pack(side="left", padx=(0, 5))
        
        # Edit client button
        self.edit_client_button = ctk.CTkButton(
            buttons_container,
            text="Edit",
            width=60,
            height=30,
            state="disabled"
        )
        self.edit_client_button.pack(side="left", padx=(0, 5))
        
        # Show archived checkbox
        self.show_archived_checkbox = ctk.CTkCheckBox(
            buttons_container,
            text="Show Archived",
            variable=self.show_archived_var,
            command=self._on_show_archived_changed,
            width=30
        )
        self.show_archived_checkbox.pack(side="left")
        
        logger.debug("Client selection row created successfully")
    
    def load_clients(self):
        """Load clients from database and populate dropdown."""
        try:
            self.clients = self.db_manager.get_clients()
            
            dropdown_values = ["Select client"]
            include_archived = self.show_archived_var.get()
            
            for client_id, first_name, last_name, is_active in self.clients:
                if include_archived:
                    # Show all clients (active and archived)
                    if is_active:
                        dropdown_values.append(f"{last_name}, {first_name}")
                    else:
                        dropdown_values.append(f"{last_name}, {first_name} (Archived)")
                else:
                    # Show only active clients
                    if is_active:
                        dropdown_values.append(f"{last_name}, {first_name}")
            
            self.client_dropdown.configure(values=dropdown_values)
            self.client_dropdown.set("Select client")
            self.selected_client_id = None
            self.edit_client_button.configure(state="disabled")
            
        except Exception as e:
            logger.error(f"Failed to load clients: {e}")
            messagebox.showerror("Database Error", f"Failed to load clients: {e}")
    
    def load_clients_and_reselect_by_id(self, client_id: int):
        """Load clients and try to reselect a specific client by ID."""
        try:
            self.clients = self.db_manager.get_clients()
            
            dropdown_values = ["Select client"]
            include_archived = self.show_archived_var.get()
            target_selection = None
            
            for c_id, first_name, last_name, is_active in self.clients:
                if include_archived:
                    # Show all clients (active and archived)
                    if is_active:
                        display_name = f"{last_name}, {first_name}"
                        dropdown_values.append(display_name)
                    else:
                        display_name = f"{last_name}, {first_name} (Archived)"
                        dropdown_values.append(display_name)
                else:
                    # Show only active clients
                    if is_active:
                        display_name = f"{last_name}, {first_name}"
                        dropdown_values.append(display_name)
                    else:
                        continue  # Skip archived clients
                
                # Check if this is the client we want to reselect
                if c_id == client_id:
                    target_selection = display_name
            
            self.client_dropdown.configure(values=dropdown_values)
            
            if target_selection:
                self.client_dropdown.set(target_selection)
                self.selected_client_id = client_id
                self.edit_client_button.configure(state="normal")
            else:
                self.client_dropdown.set("Select client")
                self.selected_client_id = None
                self.edit_client_button.configure(state="disabled")
            
        except Exception as e:
            logger.error(f"Failed to load clients and reselect: {e}")
            messagebox.showerror("Database Error", f"Failed to load clients: {e}")
    
    def _on_show_archived_changed(self):
        """Handle show archived checkbox change."""
        self.load_clients()
    
    def _on_client_selected(self, selection):
        """Handle client dropdown selection."""
        if selection == "Select client":
            self.selected_client_id = None
            self.edit_client_button.configure(state="disabled")
            return
        
        # Find the selected client
        for client_id, first_name, last_name, is_active in self.clients:
            include_archived = self.show_archived_var.get()
            
            if include_archived:
                # Looking for all clients
                if is_active:
                    client_display_name = f"{last_name}, {first_name}"
                else:
                    client_display_name = f"{last_name}, {first_name} (Archived)"
                
                if selection == client_display_name:
                    self.selected_client_id = client_id
                    self.edit_client_button.configure(state="normal")
                    break
            else:
                # Looking for active clients only
                if is_active:
                    client_display_name = f"{last_name}, {first_name}"
                    if selection == client_display_name:
                        self.selected_client_id = client_id
                        self.edit_client_button.configure(state="normal")
                        break
    
    def _on_add_client(self):
        """Handle add client button click."""
        # This will be handled by the parent frame
        pass
    
    def _on_edit_client(self):
        """Handle edit client button click."""
        # This will be handled by the parent frame
        pass
    
    def get_selected_client_id(self) -> Optional[int]:
        """Get the currently selected client ID."""
        return self.selected_client_id 
    
    def show(self):
        """Show the client selection frame."""
        if self.row_frame:
            self.row_frame.pack(fill="x", padx=PADDING, pady=(10, 5))

    def hide(self):
        """Hide the client selection frame."""
        if self.row_frame:
            self.row_frame.pack_forget() 