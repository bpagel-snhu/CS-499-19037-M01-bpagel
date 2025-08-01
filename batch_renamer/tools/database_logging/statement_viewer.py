import customtkinter as ctk
import os
import subprocess
import platform
import logging
from typing import List, Tuple
from tkinter import messagebox
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

# Local padding constant for this component
PADDING = 2


class StatementViewer:
    """Manages bank statement display and interactions."""
    
    def __init__(self, parent_frame, db_manager: DatabaseManager, main_window):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.main_window = main_window
        self.statements_scrollable = None
        self.statements_frame = None
        
    def create_statements_table_section(self):
        """Create the statements table section."""
        self.statements_frame = ctk.CTkFrame(self.parent_frame)
        # Don't pack it yet - it will be shown/hidden as needed
        
        # Table header
        header_frame = ctk.CTkFrame(self.statements_frame)
        header_frame.pack(fill="x", padx=PADDING, pady=(PADDING, 0))
        
        # Date column header
        date_header = ctk.CTkLabel(
            header_frame,
            text="Date",
            width=100,
            anchor="w"
        )
        date_header.pack(side="left", padx=PADDING, pady=PADDING)
        
        # File path column header
        file_header = ctk.CTkLabel(
            header_frame,
            text="File Path",
            anchor="w"
        )
        file_header.pack(side="left", fill="x", expand=True, padx=PADDING, pady=PADDING)
        
        # Actions column header
        actions_header = ctk.CTkLabel(
            header_frame,
            text="Actions",
            width=100,
            anchor="w"
        )
        actions_header.pack(side="right", padx=PADDING, pady=PADDING)
        
        # Scrollable frame for statements
        self.statements_scrollable = ctk.CTkScrollableFrame(
            self.statements_frame,
            height=300
        )
        self.statements_scrollable.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        logger.debug("Statements table section created successfully")
    
    def display_statements(self, statements: List[Tuple[int, str, str, str]]):
        """Display statements in the table."""
        if not self.statements_scrollable:
            return
            
        # Clear existing statements
        for widget in self.statements_scrollable.winfo_children():
            widget.destroy()
        
        if not statements:
            no_statements_label = ctk.CTkLabel(
                self.statements_scrollable,
                text="No statements found for this account.",
                text_color="gray"
            )
            no_statements_label.pack(pady=20)
            return
        
        # Display each statement
        for statement_id, account_number, statement_date, file_path in statements:
            self._create_statement_row(statement_id, statement_date, file_path)
    
    def _create_statement_row(self, statement_id: int, statement_date: str, file_path: str):
        """Create a row for a single statement."""
        row_frame = ctk.CTkFrame(self.statements_scrollable)
        row_frame.pack(fill="x", padx=PADDING, pady=2)
        
        # Date column
        date_label = ctk.CTkLabel(
            row_frame,
            text=statement_date,
            width=100,
            anchor="w"
        )
        date_label.pack(side="left", padx=PADDING, pady=PADDING)
        
        # File path column (truncated if too long)
        display_path = file_path
        if len(display_path) > 50:
            display_path = "..." + display_path[-47:]
        
        file_label = ctk.CTkLabel(
            row_frame,
            text=display_path,
            anchor="w"
        )
        file_label.pack(side="left", fill="x", expand=True, padx=PADDING, pady=PADDING)
        
        # Actions column
        actions_frame = ctk.CTkFrame(row_frame)
        actions_frame.pack(side="right", padx=PADDING, pady=PADDING)
        
        # View button
        view_button = ctk.CTkButton(
            actions_frame,
            text="View",
            width=50,
            height=25,
            command=lambda: self._view_statement(file_path)
        )
        view_button.pack(side="left", padx=(0, 5))
        
        # Delete button
        delete_button = ctk.CTkButton(
            actions_frame,
            text="Delete",
            width=50,
            height=25,
            fg_color="red",
            command=lambda: self._delete_statement(statement_id)
        )
        delete_button.pack(side="left")
    
    def _view_statement(self, file_path: str):
        """Open a statement file."""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
                
            logger.info(f"Opened statement: {file_path}")
        except Exception as e:
            logger.error(f"Failed to open statement {file_path}: {e}")
            messagebox.showerror("Error", f"Failed to open statement: {e}")
    
    def _delete_statement(self, statement_id: int):
        """Delete a statement from the database."""
        try:
            result = messagebox.askyesno(
                "Confirm Delete",
                "Are you sure you want to delete this statement? This action cannot be undone."
            )
            
            if result:
                if self.db_manager.delete_bank_statement(statement_id):
                    self.main_window.show_toast("Statement deleted successfully!")
                    # Note: The parent frame should reload statements after this
                else:
                    messagebox.showerror("Error", "Failed to delete statement.")
                    
        except Exception as e:
            logger.error(f"Failed to delete statement {statement_id}: {e}")
            messagebox.showerror("Error", f"Failed to delete statement: {e}")
    
    def show(self):
        """Show the statements frame."""
        if self.statements_frame:
            self.statements_frame.pack(fill="both", expand=True, padx=PADDING, pady=(0, 5))
    
    def hide(self):
        """Hide the statements frame."""
        if self.statements_frame:
            self.statements_frame.pack_forget() 