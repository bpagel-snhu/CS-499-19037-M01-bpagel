import sqlite3
import os
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from ...logging_config import ui_logger as logger
from ...utils import get_database_destination_from_config


class DatabaseManager:
    """Manages all database operations for the database logging tool."""
    
    def __init__(self):
        self.db_path = self._get_database_path()
        self._ensure_database_exists()
    
    def _get_database_path(self) -> str:
        """Get the database file path from config or default location."""
        db_dir = get_database_destination_from_config()
        db_dir.mkdir(parents=True, exist_ok=True)
        return str(db_dir / "clients.db")

    def _ensure_database_exists(self):
        """Create the database and tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create bank statements table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bank_statements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER NOT NULL,
                        account_number TEXT NOT NULL,
                        statement_date DATE NOT NULL,
                        file_path TEXT NOT NULL,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE,
                        UNIQUE(client_id, account_number, statement_date)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_clients(self, include_archived: bool = False) -> List[Tuple[int, str, str, bool]]:
        """Get all clients from database.
        
        Args:
            include_archived: Whether to include archived clients
            
        Returns:
            List of tuples: (id, first_name, last_name, is_active)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if include_archived:
                    cursor.execute('''
                        SELECT id, first_name, last_name, is_active 
                        FROM clients 
                        ORDER BY last_name, first_name
                    ''')
                else:
                    cursor.execute('''
                        SELECT id, first_name, last_name, is_active 
                        FROM clients 
                        WHERE is_active = 1 
                        ORDER BY last_name, first_name
                    ''')
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to load clients: {e}")
            raise

    def add_client(self, first_name: str, last_name: str, is_active: bool = True) -> int:
        """Add a new client to the database.
        
        Args:
            first_name: Client's first name
            last_name: Client's last name
            is_active: Whether the client is active
            
        Returns:
            The ID of the newly created client
            
        Raises:
            ValueError: If first_name or last_name is empty, or if client already exists
        """
        if not first_name.strip() or not last_name.strip():
            raise ValueError("First name and last name are required.")
        
        # Check for existing client with case-insensitive comparison
        if self._client_exists(first_name.strip(), last_name.strip()):
            raise ValueError(f"A client with the name '{first_name} {last_name}' already exists.")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO clients (first_name, last_name, is_active)
                    VALUES (?, ?, ?)
                ''', (first_name.strip(), last_name.strip(), is_active))
                conn.commit()
                
                client_id = cursor.lastrowid
                logger.info(f"Added client: {first_name} {last_name} (ID: {client_id})")
                return client_id
        except Exception as e:
            logger.error(f"Failed to add client: {e}")
            raise

    def _client_exists(self, first_name: str, last_name: str) -> bool:
        """Check if a client with the given name already exists (case-insensitive).
        
        Args:
            first_name: Client's first name
            last_name: Client's last name
            
        Returns:
            True if client exists, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM clients 
                    WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?)
                ''', (first_name, last_name))
                
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Failed to check if client exists: {e}")
            raise

    def update_client(self, client_id: int, first_name: str, last_name: str, is_active: bool) -> bool:
        """Update an existing client.
        
        Args:
            client_id: The ID of the client to update
            first_name: New first name
            last_name: New last name
            is_active: New active status
            
        Returns:
            True if update was successful
            
        Raises:
            ValueError: If first_name or last_name is empty, or if name conflicts with another client
        """
        if not first_name.strip() or not last_name.strip():
            raise ValueError("First name and last name are required.")
        
        # Check for existing client with case-insensitive comparison (excluding current client)
        if self._client_exists_excluding_id(first_name.strip(), last_name.strip(), client_id):
            raise ValueError(f"A client with the name '{first_name} {last_name}' already exists.")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE clients 
                    SET first_name = ?, last_name = ?, is_active = ?, updated_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (first_name.strip(), last_name.strip(), is_active, client_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Updated client ID {client_id}")
                    return True
                else:
                    logger.warning(f"Client ID {client_id} not found for update")
                    return False
        except Exception as e:
            logger.error(f"Failed to update client: {e}")
            raise

    def _client_exists_excluding_id(self, first_name: str, last_name: str, exclude_id: int) -> bool:
        """Check if a client with the given name already exists (case-insensitive), excluding a specific ID.
        
        Args:
            first_name: Client's first name
            last_name: Client's last name
            exclude_id: ID to exclude from the check (for updates)
            
        Returns:
            True if client exists, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM clients 
                    WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?) AND id != ?
                ''', (first_name, last_name, exclude_id))
                
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Failed to check if client exists: {e}")
            raise

    def get_client_by_id(self, client_id: int) -> Optional[Tuple[int, str, str, bool, str, str]]:
        """Get a client by ID.
        
        Args:
            client_id: The ID of the client to retrieve
            
        Returns:
            Tuple of (id, first_name, last_name, is_active, created_date, updated_date) or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, first_name, last_name, is_active, created_date, updated_date 
                    FROM clients 
                    WHERE id = ?
                ''', (client_id,))
                
                result = cursor.fetchone()
                return result
        except Exception as e:
            logger.error(f"Failed to get client by ID: {e}")
            raise

    def delete_client(self, client_id: int) -> bool:
        """Delete a client from the database.
        
        Args:
            client_id: The ID of the client to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Deleted client ID {client_id}")
                    return True
                else:
                    logger.warning(f"Client ID {client_id} not found for deletion")
                    return False
        except Exception as e:
            logger.error(f"Failed to delete client: {e}")
            raise

    def format_timestamp(self, timestamp_str: str) -> str:
        """Format a database timestamp into a readable format.
        
        Args:
            timestamp_str: Database timestamp string (e.g., "2024-01-15 14:30:25") in UTC
            
        Returns:
            Formatted timestamp string (e.g., "January 15, 2024 at 2:30 PM") in local timezone
        """
        try:
            # Parse the database timestamp as UTC
            dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            # Convert to local timezone
            dt_local = dt_utc.astimezone()
            # Format it in a readable way
            return dt_local.strftime("%B %d, %Y at %I:%M %p")
        except Exception as e:
            logger.error(f"Failed to format timestamp '{timestamp_str}': {e}")
            return timestamp_str  # Return original if formatting fails
    
    def add_bank_statement(self, client_id: int, account_number: str, statement_date: str, file_path: str) -> int:
        """Add a bank statement to the database.
        
        Args:
            client_id: ID of the client
            account_number: Account number from the statement
            statement_date: Date of the statement (YYYY-MM-DD format)
            file_path: Path to the PDF file
            
        Returns:
            The ID of the newly created bank statement
            
        Raises:
            ValueError: If any required field is empty or invalid
        """
        if not account_number.strip() or not statement_date.strip() or not file_path.strip():
            raise ValueError("Account number, statement date, and file path are required.")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO bank_statements (client_id, account_number, statement_date, file_path)
                    VALUES (?, ?, ?, ?)
                ''', (client_id, account_number.strip(), statement_date.strip(), file_path.strip()))
                conn.commit()
                
                statement_id = cursor.lastrowid
                logger.info(f"Added bank statement: {account_number} - {statement_date} for client {client_id}")
                return statement_id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"A statement for account {account_number} on {statement_date} already exists for this client.")
            else:
                raise
        except Exception as e:
            logger.error(f"Failed to add bank statement: {e}")
            raise
    
    def get_bank_statements(self, client_id: int) -> List[Tuple[int, str, str, str]]:
        """Get all bank statements for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            List of tuples: (id, account_number, statement_date, file_path)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, account_number, statement_date, file_path 
                    FROM bank_statements 
                    WHERE client_id = ? 
                    ORDER BY statement_date DESC
                ''', (client_id,))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to load bank statements: {e}")
            raise

    def get_accounts_for_client(self, client_id: int) -> List[str]:
        """Get all unique account numbers for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            List of account numbers
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT account_number 
                    FROM bank_statements 
                    WHERE client_id = ? 
                    ORDER BY account_number
                ''', (client_id,))
                
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to load accounts: {e}")
            raise

    def get_bank_statements_by_account(self, client_id: int, account_number: str) -> List[Tuple[int, str, str, str]]:
        """Get all bank statements for a specific account.
        
        Args:
            client_id: The client ID
            account_number: The account number
            
        Returns:
            List of tuples: (id, account_number, statement_date, file_path)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, account_number, statement_date, file_path 
                    FROM bank_statements 
                    WHERE client_id = ? AND account_number = ?
                    ORDER BY statement_date DESC
                ''', (client_id, account_number))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to load bank statements by account: {e}")
            raise

    def get_total_statements_for_client(self, client_id: int) -> int:
        """Get the total number of statements for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            Total number of statements for the client
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM bank_statements 
                    WHERE client_id = ?
                ''', (client_id,))
                
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get total statements for client: {e}")
            raise
    
    def delete_bank_statement(self, statement_id: int) -> bool:
        """Delete a bank statement from the database.
        
        Args:
            statement_id: ID of the statement to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM bank_statements WHERE id = ?', (statement_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Deleted bank statement: {statement_id}")
                    return True
                else:
                    logger.warning(f"Bank statement not found: {statement_id}")
                    return False
        except Exception as e:
            logger.error(f"Failed to delete bank statement: {e}")
            raise 