import unittest
import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
from pathlib import Path
from tests.unit.test_base import MessageboxPatchedTestCase
from batch_renamer.utils import (
    get_backup_directory,
    ensure_directory_exists,
    get_file_extension,
    is_valid_directory
)

@pytest.mark.functional
class TestUtils(MessageboxPatchedTestCase):
    """Tests for utility functions."""
    
    def setUp(self):
        """Set up each test."""
        super().setUp()
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
        super().tearDown()
        
    def test_get_backup_directory(self):
        """Test backup directory creation and retrieval."""
        # Test that backup directory is created in Downloads
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path(self.test_dir)
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                mock_mkdir.return_value = None
                backup_dir = get_backup_directory()
                self.assertEqual(backup_dir, Path(self.test_dir) / "Downloads" / "Renamer Backups")
                mock_mkdir.assert_called_once_with(exist_ok=True)
            
    def test_ensure_directory_exists(self):
        """Test directory creation and existence checking."""
        # Test creating a new directory
        new_dir = os.path.join(self.test_dir, "new_dir")
        ensure_directory_exists(new_dir)
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
        
        # Test with nested directories
        nested_dir = os.path.join(self.test_dir, "nested", "deep", "dir")
        ensure_directory_exists(nested_dir)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.isdir(nested_dir))
        
    def test_get_file_extension(self):
        """Test file extension extraction."""
        # Test with various file extensions
        test_cases = [
            ("test.pdf", ".pdf"),
            ("document.docx", ".docx"),
            ("image.PNG", ".PNG"),
            ("no_extension", ""),
            (".hidden_file", ""),
            ("multiple.dots.in.name.txt", ".txt")
        ]
        
        for filename, expected in test_cases:
            self.assertEqual(get_file_extension(filename), expected)
            
    def test_is_valid_directory(self):
        """Test directory validation."""
        # Test with valid directory
        self.assertTrue(is_valid_directory(self.test_dir))
        
        # Test with non-existent directory
        self.assertFalse(is_valid_directory(os.path.join(self.test_dir, "nonexistent")))
        
        # Test with file instead of directory
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        self.assertFalse(is_valid_directory(test_file))
        
        # Test with empty string
        self.assertFalse(is_valid_directory(""))
        
        # Test with None
        self.assertFalse(is_valid_directory(None))

if __name__ == '__main__':
    unittest.main() 