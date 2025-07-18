import unittest
import os
import shutil
import tempfile
from unittest.mock import patch
import pytest

from batch_renamer.rename_logic import (
    parse_filename_position_based,
    build_new_filename,
    rename_files_in_folder,
    ParseError,
    ValidationError
)

@pytest.mark.functional
class TestRenameLogic(unittest.TestCase):
    """Tests for core rename logic functionality, independent of GUI."""
    
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create some test PDF files
        self.test_files = []
        for i in range(3):
            filename = f"doc2024{i+1:02d}15.pdf"  # doc20240115.pdf, doc20240215.pdf, etc.
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            self.test_files.append(file_path)

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
        # Clean up test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_parse_filename_position_based(self):
        """Test parsing filenames with position-based extraction."""
        # Test with numeric month
        filename = "doc20240115.pdf"
        year, month, day = parse_filename_position_based(
            filename,
            year_start=3,
            year_length=4,
            month_start=7,
            month_length=2,
            day_start=9,
            day_length=2
        )
        self.assertEqual(year, "2024")
        self.assertEqual(month, "01")
        self.assertEqual(day, "15")

        # Test with textual month (using abbreviation)
        filename = "doc2024Jan15.pdf"
        year, month, day = parse_filename_position_based(
            filename,
            year_start=3,
            year_length=4,
            month_start=7,
            month_length=3,
            day_start=10,
            day_length=2,
            textual_month=True
        )
        self.assertEqual(year, "2024")
        self.assertEqual(month, "01")
        self.assertEqual(day, "15")

        # Test with full month name
        filename = "doc2024January15.pdf"
        year, month, day = parse_filename_position_based(
            filename,
            year_start=3,
            year_length=4,
            month_start=7,
            month_length=7,  # Length of "January"
            day_start=14,
            day_length=2,
            textual_month=True
        )
        self.assertEqual(year, "2024")
        self.assertEqual(month, "01")
        self.assertEqual(day, "15")

        # Test with invalid month
        filename = "doc2024Invalid15.pdf"
        with self.assertRaises(ParseError):
            parse_filename_position_based(
                filename,
                year_start=3,
                year_length=4,
                month_start=7,
                month_length=7,
                day_start=14,
                day_length=2,
                textual_month=True
            )

    def test_parse_filename_invalid_positions(self):
        """Test parsing with invalid position parameters."""
        filename = "short.pdf"
        with self.assertRaises(ParseError):
            parse_filename_position_based(
                filename,
                year_start=10,  # Beyond string length
                year_length=4,
                month_start=14,
                month_length=2
            )

    def test_build_new_filename(self):
        """Test building new filenames with various components."""
        # Test with all parts
        result = build_new_filename("DOC_", "2024", "01", "15", separator="_")
        self.assertEqual(result, "DOC_2024_01_15")

        # Test without prefix
        result = build_new_filename("", "2024", "01", "15")
        self.assertEqual(result, "20240115")

        # Test without day
        result = build_new_filename("DOC_", "2024", "01", "")
        self.assertEqual(result, "DOC_202401")

    def test_rename_files_in_folder(self):
        """Test the core file renaming functionality."""
        # Clean up any existing test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        self.test_files.clear()

        # Create test files with specific names
        test_files = []
        for i in range(3):
            filename = f"doc2024{i+1:02d}15.pdf"  # doc20240115.pdf, doc20240215.pdf, etc.
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(file_path)
            self.test_files.append(file_path)  # Add to test_files for cleanup

        # Verify files were created
        for file_path in test_files:
            self.assertTrue(os.path.exists(file_path), f"Test file {file_path} was not created")

        position_args = {
            'year_start': 3,
            'year_length': 4,
            'month_start': 7,
            'month_length': 2,
            'day_start': 9,
            'day_length': 2
        }

        # Ensure the test directory exists and is writable
        self.assertTrue(os.path.exists(self.test_dir), "Test directory does not exist")
        self.assertTrue(os.access(self.test_dir, os.W_OK), "Test directory is not writable")

        result = rename_files_in_folder(
            self.test_dir,
            prefix="NEW_",
            position_args=position_args,
            expected_length=11,  # Length of "doc20240115" (without extension)
            dry_run=False,
            textual_month=False
        )

        # Verify the result structure
        self.assertIsInstance(result, dict)
        self.assertIn('total', result)
        self.assertIn('renamed', result)
        self.assertIn('skipped', result)
        self.assertIn('successful', result)
        self.assertIn('failed', result)

        # Verify the counts
        self.assertEqual(result['total'], 3)
        self.assertEqual(len(result['renamed']), 3)

        # Verify the files were actually renamed
        for old_path, new_path in result['renamed'].items():
            self.assertFalse(os.path.exists(old_path), f"Old file {old_path} still exists")
            self.assertTrue(os.path.exists(new_path), f"New file {new_path} does not exist")

    def test_rename_files_validation(self):
        """Test input validation for rename operations."""
        # Test with invalid folder
        with self.assertRaises(ValidationError):
            rename_files_in_folder(
                "nonexistent_folder",
                prefix="TEST_",
                position_args={},
                expected_length=10
            )

        # Test without position_args
        with self.assertRaises(ValidationError):
            rename_files_in_folder(
                self.test_dir,
                prefix="TEST_",
                position_args=None,
                expected_length=10
            )

        # Test without expected_length
        with self.assertRaises(ValidationError):
            rename_files_in_folder(
                self.test_dir,
                prefix="TEST_",
                position_args={},
                expected_length=None
            )

if __name__ == '__main__':
    unittest.main() 