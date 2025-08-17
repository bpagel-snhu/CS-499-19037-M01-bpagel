import customtkinter as ctk
import logging
from typing import List, Tuple
from tkinter import messagebox
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

# Local padding constant for this component
PADDING = 2


class AccountOverview:
    """Manages account overview display showing account information and statistics."""
    
    def __init__(self, parent_frame, db_manager: DatabaseManager, main_window):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.main_window = main_window
        self.overview_frame = None
        self.accounts_scrollable = None
        
    def create_account_overview_section(self):
        """Create the account overview section."""
        self.overview_frame = ctk.CTkFrame(self.parent_frame)
        # Don't pack it yet - it will be shown/hidden as needed
        
        # Create a main frame that will contain both header and data
        self.main_table_frame = ctk.CTkFrame(self.overview_frame)
        self.main_table_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
        
        # Configure grid weights for proper column sizing
        self.main_table_frame.grid_columnconfigure(0, weight=0, minsize=20)  # Account column
        self.main_table_frame.grid_columnconfigure(1, weight=0, minsize=100)  # Statements column
        self.main_table_frame.grid_columnconfigure(2, weight=1, minsize=200)  # Date range column (expandable)
        
        # Section header
        header_frame = ctk.CTkFrame(self.main_table_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=(0, 1))
        
        # Configure header frame grid
        header_frame.grid_columnconfigure(0, weight=0, minsize=20)
        header_frame.grid_columnconfigure(1, weight=0, minsize=100)
        header_frame.grid_columnconfigure(2, weight=1, minsize=200)
        
        # Account column header
        account_header = ctk.CTkLabel(
            header_frame,
            text="Acct",
            anchor="w"
        )
        account_header.grid(row=0, column=0, sticky="ew", padx=4, pady=2)
        
        # Statement count column header
        count_header = ctk.CTkLabel(
            header_frame,
            text="Statements",
            anchor="w"
        )
        count_header.grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        
        # Date range column header
        date_header = ctk.CTkLabel(
            header_frame,
            text="Date Range",
            anchor="w"
        )
        date_header.grid(row=0, column=2, sticky="ew", padx=4, pady=2)
        
        # Scrollable frame for accounts
        self.accounts_scrollable = ctk.CTkScrollableFrame(
            self.main_table_frame,
            height=300
        )
        self.accounts_scrollable.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)
        
        # Configure scrollable frame grid
        self.accounts_scrollable.grid_columnconfigure(0, weight=0, minsize=80)
        self.accounts_scrollable.grid_columnconfigure(1, weight=0, minsize=100)
        self.accounts_scrollable.grid_columnconfigure(2, weight=1, minsize=200)
        
        logger.debug("Account overview section created successfully")
    
    def display_accounts(self, accounts_data: List[Tuple[str, int, str, str]]):
        """Display account overview information.
        
        Args:
            accounts_data: List of tuples (account_number, statement_count, oldest_date, newest_date)
        """
        # Clear existing content
        for widget in self.accounts_scrollable.winfo_children():
            widget.destroy()
        
        if not accounts_data:
            # Show "no accounts" message
            no_accounts_label = ctk.CTkLabel(
                self.accounts_scrollable,
                text="No accounts found for this client.",
                anchor="center"
            )
            no_accounts_label.pack(pady=20)
            return
        
        # Create rows for each account
        for account_number, statement_count, oldest_date, newest_date in accounts_data:
            self._create_account_row(account_number, statement_count, oldest_date, newest_date)
    
    def _create_account_row(self, account_number: str, statement_count: int, oldest_date: str, newest_date: str):
        """Create a row displaying account information."""
        # Get the current row number
        row_num = len(self.accounts_scrollable.winfo_children())
        
        # Account number (add 'x' prefix if not present)
        display_account = f"x{account_number}" if not account_number.startswith('x') else account_number
        account_label = ctk.CTkLabel(
            self.accounts_scrollable,
            text=display_account,
            anchor="e",
            height=20
        )
        account_label.grid(row=row_num, column=0, sticky="ew", padx=4, pady=1)
        
        # Statement count
        count_label = ctk.CTkLabel(
            self.accounts_scrollable,
            text=str(statement_count),
            anchor="w",
            height=20
        )
        count_label.grid(row=row_num, column=1, sticky="ew", padx=4, pady=1)
        
        # Date range
        date_range_text = f"{oldest_date} to {newest_date}" if oldest_date != newest_date else oldest_date
        date_label = ctk.CTkLabel(
            self.accounts_scrollable,
            text=date_range_text,
            anchor="w",
            height=20
        )
        date_label.grid(row=row_num, column=2, sticky="ew", padx=4, pady=1)
        

    

    

    
    def show(self):
        """Show the account overview frame."""
        if self.overview_frame:
            self.overview_frame.pack(fill="both", expand=True, padx=PADDING, pady=(0, 5))
    
    def hide(self):
        """Hide the account overview frame."""
        if self.overview_frame:
            self.overview_frame.pack_forget()
