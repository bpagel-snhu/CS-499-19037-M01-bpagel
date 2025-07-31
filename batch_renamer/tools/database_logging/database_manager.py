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
            ValueError: If first_name or last_name is empty
        """
        if not first_name.strip() or not last_name.strip():
            raise ValueError("First name and last name are required.")
        
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
            ValueError: If first_name or last_name is empty
        """
        if not first_name.strip() or not last_name.strip():
            raise ValueError("First name and last name are required.")
        
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