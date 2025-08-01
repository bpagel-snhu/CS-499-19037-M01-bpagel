import os
import re
import logging
from typing import Tuple, List
from tkinter import messagebox
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ImportManager:
    """Manages bank statement import operations."""
    
    def __init__(self, db_manager: DatabaseManager, main_window):
        self.db_manager = db_manager
        self.main_window = main_window
    
    def import_statements_from_folder(self, folder_path: str, client_id: int) -> Tuple[int, int]:
        """Import bank statements from a folder for a specific client.
        
        Args:
            folder_path: Path to the folder containing statements
            client_id: ID of the client to associate statements with
            
        Returns:
            Tuple of (imported_count, total_found)
        """
        try:
            imported_count, total_found = self._parse_and_import_statements(folder_path, client_id)
            
            # Show appropriate feedback
            if imported_count > 0:
                client_name = self._get_client_name(client_id)
                self.main_window.show_toast(f"Found {imported_count} new statements - added to {client_name}'s profile!")
            elif total_found > 0:
                self.main_window.show_toast("No new statements found.")
            else:
                self.main_window.show_toast("No matching bank statements found in the selected folder.")
                
            return imported_count, total_found
            
        except Exception as e:
            logger.error(f"Failed to import statements: {e}")
            messagebox.showerror("Import Error", f"Failed to import statements: {e}")
            return 0, 0
    
    def _parse_and_import_statements(self, folder_path: str, client_id: int) -> Tuple[int, int]:
        """Parse PDF files and import bank statements to database.
        
        Args:
            folder_path: Path to the folder containing statements
            client_id: ID of the client to associate statements with
            
        Returns:
            Tuple of (imported_count, total_found)
        """
        imported_count = 0
        total_found = 0
        
        # Updated pattern to match: x[ACCOUNT] - [YYYY][MM][DD].pdf or x[ACCOUNT] - [YYYY][MM].pdf
        # Account can be alphanumeric, date can be 6 digits (YYYYMM) or 8 digits (YYYYMMDD)
        pattern_8digit = r'^x([a-zA-Z0-9]+)\s*-\s*(\d{4})(\d{2})(\d{2})\.pdf$'
        pattern_6digit = r'^x([a-zA-Z0-9]+)\s*-\s*(\d{4})(\d{2})\.pdf$'
        
        # Recursively search for PDF files
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    # Try 8-digit date pattern first (YYYYMMDD)
                    match = re.match(pattern_8digit, file)
                    if match:
                        account_number = match.group(1)
                        year = match.group(2)
                        month = match.group(3)
                        day = match.group(4)
                        
                        # Format date as YYYY-MM-DD
                        statement_date = f"{year}-{month}-{day}"
                        file_path = os.path.join(root, file)
                        
                        total_found += 1
                        
                        try:
                            # Add to database
                            self.db_manager.add_bank_statement(
                                client_id,
                                account_number,
                                statement_date,
                                file_path
                            )
                            imported_count += 1
                            logger.info(f"Imported statement: {account_number} - {statement_date}")
                            
                        except ValueError as e:
                            # Statement already exists, skip
                            logger.warning(f"Skipped duplicate statement: {account_number} - {statement_date}")
                        except Exception as e:
                            logger.error(f"Failed to import statement {file}: {e}")
                    
                    # Try 6-digit date pattern (YYYYMM)
                    else:
                        match = re.match(pattern_6digit, file)
                        if match:
                            account_number = match.group(1)
                            year = match.group(2)
                            month = match.group(3)
                            
                            # For 6-digit dates, assume day 01
                            statement_date = f"{year}-{month}-01"
                            file_path = os.path.join(root, file)
                            
                            total_found += 1
                            
                            try:
                                # Add to database
                                self.db_manager.add_bank_statement(
                                    client_id,
                                    account_number,
                                    statement_date,
                                    file_path
                                )
                                imported_count += 1
                                logger.info(f"Imported statement: {account_number} - {statement_date}")
                                
                            except ValueError as e:
                                # Statement already exists, skip
                                logger.warning(f"Skipped duplicate statement: {account_number} - {statement_date}")
                            except Exception as e:
                                logger.error(f"Failed to import statement {file}: {e}")
        
        return imported_count, total_found
    
    def _get_client_name(self, client_id: int) -> str:
        """Get client name for display purposes."""
        try:
            client = self.db_manager.get_client_by_id(client_id)
            if client:
                first_name, last_name = client[1], client[2]
                return f"{first_name} {last_name}"
            return "Unknown Client"
        except Exception as e:
            logger.error(f"Failed to get client name: {e}")
            return "Unknown Client" 