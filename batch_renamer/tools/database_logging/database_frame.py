import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import List, Tuple, Optional
import os
import re
from datetime import datetime

from ...ui_utils import create_button
from ...logging_config import ui_logger as logger
from .database_manager import DatabaseManager
from .dialogs.add_client_dialog import AddClientDialog
from .dialogs.edit_client_dialog import EditClientDialog
from .import_manager import ImportManager
from .account_overview import AccountOverview
from .client_selection import ClientSelection
from .account_selection import AccountSelection


class DatabaseFrame(ctk.CTkFrame):
    """
    Database tool frame for managing client information and bank statement tracking.
    """

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.db_manager = DatabaseManager()
        
        # Initialize managers and components
        self.import_manager = ImportManager(self.db_manager, main_window)
        self.client_selection = ClientSelection(self, self.db_manager, main_window)
        self.account_selection = AccountSelection(self, self.db_manager, main_window)
        self.account_overview = AccountOverview(self, self.db_manager, main_window)
        
        # Initialize variables
        self.selected_folder = None
        self.folder_header_frame = None
        
        # Create widgets
        self._create_widgets()
        
        # Load initial data
        self.client_selection.load_clients()

    def _create_widgets(self):
        """Create all UI widgets for the database frame."""
        logger.debug("Creating database frame widgets")

        # Create the client selection row (this will be visible)
        self.client_selection.create_client_selection_row()
        self.client_selection.show()  # Show the client selection frame
        
        # Set up callbacks for client selection
        self.client_selection.client_dropdown.configure(command=self._on_client_selected)
        self.client_selection.add_client_button.configure(command=self._on_add_client)
        self.client_selection.edit_client_button.configure(command=self._on_edit_client)

        # Create account selection section (initially hidden)
        self.account_selection.create_account_selection_section()
        
        # Set up callbacks for account selection
        self.account_selection.set_import_callback(self._on_import_statements)
        self.account_selection.set_export_callback(self._on_export_all_statements)
        
        # Create account overview section (initially hidden)
        self.account_overview.create_account_overview_section()
        
        # Initially hide account and overview sections
        self.account_selection.hide()
        self.account_overview.hide()

    def _load_account_overview_for_client(self, client_id: int):
        """Load account overview for a specific client."""
        try:
            accounts_data = self.db_manager.get_account_overview_for_client(client_id)
            self.account_overview.display_accounts(accounts_data)
        except Exception as e:
            logger.error(f"Failed to load account overview: {e}")
            messagebox.showerror("Database Error", f"Failed to load account overview: {e}")

    def _on_client_selected(self, selection):
        """Handle client selection."""
        if selection == "Select client":
            self._hide_account_section()
            return
        
        # Find the selected client
        for client_id, first_name, last_name, is_active in self.client_selection.clients:
            include_archived = self.client_selection.show_archived_var.get()
            
            # Check if this client matches the current filter and selection
            if include_archived:
                # Looking for archived clients
                if not is_active:
                    client_display_name = f"{last_name}, {first_name} (Archived)"
                    if selection == client_display_name:
                        self.client_selection.selected_client_id = client_id
                        self.client_selection.edit_client_button.configure(state="normal")
                        self._show_account_section()
                        logger.info(f"Selected client: {first_name} {last_name} (ID: {client_id})")
                        break
            else:
                # Looking for active clients
                if is_active:
                    client_display_name = f"{last_name}, {first_name}"
                    if selection == client_display_name:
                        self.client_selection.selected_client_id = client_id
                        self.client_selection.edit_client_button.configure(state="normal")
                        self._show_account_section()
                        logger.info(f"Selected client: {first_name} {last_name} (ID: {client_id})")
                        break

    def _show_account_section(self):
        """Show the account section when a client is selected."""
        self.account_selection.show()
        self.account_overview.show()
        
        # Load account overview for the selected client
        client_id = self.client_selection.get_selected_client_id()
        if client_id:
            self._load_account_overview_for_client(client_id)
            self.account_selection.load_accounts_for_client(client_id)
    
    def _hide_account_section(self):
        """Hide the account section when no client is selected."""
        self.account_selection.hide()
        self.account_overview.hide()

    def _on_import_statements(self):
        """Handle import statements button click."""
        client_id = self.client_selection.get_selected_client_id()
        if not client_id:
            messagebox.showerror("Error", "Please select a client first.")
            return
        
        # Open folder selection dialog
        folder_path = filedialog.askdirectory(title="Select folder containing bank statements")
        if folder_path:
            self.selected_folder = folder_path
            logger.info(f"Selected folder: {folder_path}")
            
            # Use the import manager to handle the import
            self.import_manager.import_statements_from_folder(self.selected_folder, client_id)
            
            # Reload account overview to update statistics
            self._load_account_overview_for_client(client_id)
            self.account_selection.load_accounts_for_client(client_id)

    def _on_export_all_statements(self):
        """Handle export all statements button click."""
        client_id = self.client_selection.get_selected_client_id()
        if not client_id:
            messagebox.showerror("Error", "Please select a client first.")
            return
        
        try:
            # Get all statements for the client
            statements = self.db_manager.get_bank_statements(client_id)
            
            if not statements:
                messagebox.showinfo("Info", "No statements found for this client.")
                return
            
            # Ask user for save location
            from datetime import datetime
            filename = f"all_statements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = filedialog.asksaveasfilename(
                title="Export All Statements",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=filename
            )
            
            if file_path:
                # Write to CSV
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Statement ID', 'Account Number', 'Statement Date', 'File Path'])
                    for statement_id, account_number, statement_date, file_path in statements:
                        # Add 'x' prefix to account number if not present
                        display_account = f"x{account_number}" if not account_number.startswith('x') else account_number
                        writer.writerow([statement_id, display_account, statement_date, file_path])
                
                self.main_window.show_toast(f"Exported {len(statements)} statements successfully!")
                logger.info(f"Exported {len(statements)} statements for client {client_id} to {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to export statements: {e}")
            messagebox.showerror("Export Error", f"Failed to export statements: {e}")

    def _on_add_client(self):
        """Open add client dialog."""
        self._show_add_client_dialog()

    def _on_edit_client(self):
        """Open edit client dialog."""
        client_id = self.client_selection.get_selected_client_id()
        if client_id is not None:
            self._show_edit_client_dialog()

    def _show_add_client_dialog(self):
        """Show dialog to add a new client."""
        dialog = AddClientDialog(self, self.db_manager)
        self.wait_window(dialog)
        if dialog.result:
            self.client_selection.load_clients()
            # Show success toast
            self.main_window.show_toast("Client added successfully!")

    def _show_edit_client_dialog(self):
        """Show dialog to edit the selected client."""
        client_id = self.client_selection.get_selected_client_id()
        if client_id is not None:
            # Get the full client data from the database
            client_data = self.db_manager.get_client_by_id(client_id)
            if client_data is not None:
                dialog = EditClientDialog(self, self.db_manager, client_data)
                self.wait_window(dialog)
                
                if dialog.result == "updated":
                    # Reload clients and reselect the edited client
                    self.client_selection.load_clients_and_reselect_by_id(client_id)
                    self.main_window.show_toast("Client updated successfully!")
                elif dialog.result == "deleted":
                    # Reload clients and clear selection
                    self.client_selection.load_clients()
                    self._hide_account_section()
                    self.main_window.show_toast("Client deleted successfully!")
            else:
                messagebox.showerror("Error", "Client not found in database.")

 