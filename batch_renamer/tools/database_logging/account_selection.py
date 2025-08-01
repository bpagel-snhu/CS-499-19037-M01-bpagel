import customtkinter as ctk
import logging
from typing import List, Optional
from tkinter import messagebox
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

# Local padding constant for this component
PADDING = 2


class AccountSelection:
    """Manages account selection dropdown and related functionality."""
    
    def __init__(self, parent_frame, db_manager: DatabaseManager, main_window):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.main_window = main_window
        self.selected_account = None
        
        # UI elements
        self.account_frame = None
        self.account_dropdown = None
        self.stats_label = None
        self.import_button = None
        
    def create_account_selection_section(self):
        """Create the account selection section with statistics and import button."""
        self.account_frame = ctk.CTkFrame(self.parent_frame)
        # Don't pack it yet - it will be shown/hidden as needed
        
        # Statistics label (left side)
        self.stats_label = ctk.CTkLabel(
            self.account_frame,
            text="0 Total Statements / 0 Accounts Found",
            anchor="w"
        )
        self.stats_label.pack(side="left", padx=PADDING, pady=PADDING)
        
        # Account selection dropdown (center)
        self.account_dropdown = ctk.CTkComboBox(
            self.account_frame,
            values=["Select account"],
            command=self._on_account_selected,
            state="readonly",
            width=200
        )
        self.account_dropdown.pack(side="left", padx=PADDING, pady=PADDING)
        
        # Import button (right side)
        self.import_button = ctk.CTkButton(
            self.account_frame,
            text="Import",
            width=120
        )
        self.import_button.pack(side="right", padx=PADDING, pady=PADDING)
        
        logger.debug("Account selection section created successfully")
    
    def load_accounts_for_client(self, client_id: int):
        """Load accounts for a specific client and update statistics."""
        try:
            accounts = self.db_manager.get_accounts_for_client(client_id)
            total_statements = self.db_manager.get_total_statements_for_client(client_id)
            
            if accounts:
                dropdown_values = ["Select account"]
                for account in accounts:
                    dropdown_values.append(account)
                
                self.account_dropdown.configure(values=dropdown_values)
                self.account_dropdown.set("Select account")
                self.selected_account = None
                
                # Update statistics
                self.stats_label.configure(text=f"{total_statements} Total Statements / {len(accounts)} Accounts Found")
            else:
                self.account_dropdown.configure(values=["Select account"])
                self.account_dropdown.set("Select account")
                self.selected_account = None
                
                # Update statistics
                self.stats_label.configure(text="0 Total Statements / 0 Accounts Found")
                
        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
            messagebox.showerror("Database Error", f"Failed to load accounts: {e}")
    
    def set_import_callback(self, callback):
        """Set the callback for the import button."""
        if self.import_button:
            self.import_button.configure(command=callback)
    
    def _on_account_selected(self, selection):
        """Handle account selection."""
        if selection == "Select account":
            self.selected_account = None
            return
        
        self.selected_account = selection
        logger.info(f"Selected account: {selection}")
    
    def get_selected_account(self) -> Optional[str]:
        """Get the currently selected account."""
        return self.selected_account
    
    def show(self):
        """Show the account selection frame."""
        if self.account_frame:
            self.account_frame.pack(fill="x", padx=PADDING, pady=(0, 5))
    
    def hide(self):
        """Hide the account selection frame."""
        if self.account_frame:
            self.account_frame.pack_forget() 