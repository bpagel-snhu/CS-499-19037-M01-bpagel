import pytest
import sqlite3
import os
import tempfile
import shutil
from unittest.mock import Mock, patch

from batch_renamer.tools.database_logging.database_manager import DatabaseManager


class TestDatabaseManager:
    """Test cases for database manager functionality."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_clients.db")
        yield db_path
        # Clean up after tests
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # On Windows, files might still be in use
            pass

    def test_database_creation(self, temp_db_path):
        """Test that the database and tables are created correctly."""
        with patch('batch_renamer.tools.database_logging.database_manager.DatabaseManager._get_database_path', return_value=temp_db_path):
            # Create manager
            manager = DatabaseManager()
            
            # Check that database file exists
            assert os.path.exists(temp_db_path)
            
            # Check that clients table exists and has correct structure
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(clients)")
                columns = cursor.fetchall()
                
                # Check column names and types
                column_names = [col[1] for col in columns]
                assert 'id' in column_names
                assert 'first_name' in column_names
                assert 'last_name' in column_names
                assert 'is_active' in column_names
                assert 'created_date' in column_names
                assert 'updated_date' in column_names

    def test_add_client_to_database(self, temp_db_path):
        """Test adding a new client to the database."""
        with patch('batch_renamer.tools.database_logging.database_manager.DatabaseManager._get_database_path', return_value=temp_db_path):
            manager = DatabaseManager()
            
            # Add a test client
            client_id = manager.add_client("John", "Doe", True)
            
            # Verify client was added
            clients = manager.get_clients()
            assert len(clients) == 1
            assert clients[0][1] == "John"  # first_name
            assert clients[0][2] == "Doe"   # last_name
            assert clients[0][3] == True    # is_active

    def test_load_clients_from_database(self, temp_db_path):
        """Test loading clients from database."""
        with patch('batch_renamer.tools.database_logging.database_manager.DatabaseManager._get_database_path', return_value=temp_db_path):
            manager = DatabaseManager()
            
            # Add test clients
            manager.add_client("John", "Doe", True)
            manager.add_client("Jane", "Smith", False)
            
            # Test loading all clients
            clients = manager.get_clients(include_archived=True)
            
            # Check that clients were loaded correctly
            assert len(clients) == 2
            assert clients[0][1] == "John"  # first_name
            assert clients[0][2] == "Doe"   # last_name
            assert clients[0][3] == True    # is_active
            assert clients[1][1] == "Jane"  # first_name
            assert clients[1][2] == "Smith" # last_name
            assert clients[1][3] == False   # is_active

    def test_filter_active_clients(self, temp_db_path):
        """Test filtering to show only active clients."""
        with patch('batch_renamer.tools.database_logging.database_manager.DatabaseManager._get_database_path', return_value=temp_db_path):
            manager = DatabaseManager()
            
            # Add test clients
            manager.add_client("John", "Doe", True)
            manager.add_client("Jane", "Smith", False)
            
            # Test with archived hidden (only active clients)
            active_clients = manager.get_clients(include_archived=False)
            assert len(active_clients) == 1
            assert active_clients[0][1] == "John"  # Only active client
            
            # Test with archived shown (all clients)
            all_clients = manager.get_clients(include_archived=True)
            assert len(all_clients) == 2  # Both clients

    def test_add_client_dialog_logic(self, temp_db_path):
        """Test the logic for adding a client through the dialog."""
        with patch('batch_renamer.tools.database_logging.database_manager.DatabaseManager._get_database_path', return_value=temp_db_path):
            manager = DatabaseManager()
            
            # Test adding a client
            first_name = "John"
            last_name = "Doe"
            is_active = True
            
            client_id = manager.add_client(first_name, last_name, is_active)
            
            # Verify client was added
            clients = manager.get_clients()
            assert len(clients) == 1
            assert clients[0][1] == first_name
            assert clients[0][2] == last_name
            assert clients[0][3] == is_active

    def test_validation_logic(self, temp_db_path):
        """Test validation logic for client data."""
        with patch('batch_renamer.tools.database_logging.database_manager.DatabaseManager._get_database_path', return_value=temp_db_path):
            manager = DatabaseManager()
            
            # Test empty first name
            with pytest.raises(ValueError, match="First name and last name are required"):
                manager.add_client("", "Doe")
            
            # Test empty last name
            with pytest.raises(ValueError, match="First name and last name are required"):
                manager.add_client("John", "")
            
            # Test valid data
            client_id = manager.add_client("John", "Doe")
            assert client_id > 0 