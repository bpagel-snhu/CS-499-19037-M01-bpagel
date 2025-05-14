import unittest
import os
import shutil
import tempfile
from pathlib import Path
import pytest

from batch_renamer.ui.month_normalize import (
    count_full_months_in_folder,
    normalize_full_months_in_folder
)
from batch_renamer.exceptions import ValidationError, FileOperationError

@pytest.mark.functional
class TestMonthNormalize(unittest.TestCase):
    """Tests for month name normalization functionality."""
    
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Abbreviated months (including May)
        self.abbr_months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        # Full months (excluding May)
        self.full_months = [
            "January", "February", "March", "April", "June", "July", "August", "September", "October", "November", "December"
        ]

        self.abbr_files = []
        self.full_files = []

        # Create files with abbreviated months
        for abbr in self.abbr_months:
            filename = f"report_{abbr}_2024.pdf"
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Abbreviated month: {abbr}")
            self.abbr_files.append(file_path)

        # Create files with full month names (excluding May)
        for month in self.full_months:
            filename = f"report_{month}_2024.pdf"
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Full month: {month}")
            self.full_files.append(file_path)

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_count_full_months_in_folder(self):
        """Test counting files with full month names."""
        # Should find all files with full month names
        count = count_full_months_in_folder(self.test_dir)
        self.assertEqual(count, len(self.full_files))

        # Test with empty folder
        empty_dir = tempfile.mkdtemp()
        try:
            count = count_full_months_in_folder(empty_dir)
            self.assertEqual(count, 0)
        finally:
            shutil.rmtree(empty_dir)

        # Test with invalid folder
        with self.assertRaises(ValidationError):
            count_full_months_in_folder("nonexistent_folder")

    def test_normalize_full_months_in_folder(self):
        """Test normalizing full month names to abbreviations, skipping already abbreviated files."""
        # Run normalization
        renamed_count = normalize_full_months_in_folder(self.test_dir)

        # Expected: all full month files (excluding May) are renamed
        expected_renames = len(self.full_files)
        self.assertEqual(renamed_count, expected_renames)

        # Abbreviated files should remain unchanged
        for file_path in self.abbr_files:
            self.assertTrue(os.path.exists(file_path), f"Abbreviated file {file_path} should not be renamed")

        # Full month files should be renamed to their abbreviations
        for old_path, month in zip(self.full_files, self.full_months):
            abbr = month[:3]
            new_filename = os.path.basename(old_path).replace(month, abbr)
            new_path = os.path.join(self.test_dir, new_filename)
            self.assertTrue(os.path.exists(new_path), f"Expected file {new_filename} not found")
            self.assertFalse(os.path.exists(old_path), f"Old file {old_path} still exists")

    def test_normalize_full_months_with_collisions(self):
        """Test handling of filename collisions during normalization"""
        # Clean up existing test files
        for file_path in self.full_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        self.full_files.clear()
        
        # Create a file that will cause a collision
        with open(os.path.join(self.test_dir, "doc_Jan_2024.pdf"), "w") as f:
            f.write("Original file")
        
        # Create a file that will collide
        with open(os.path.join(self.test_dir, "doc_January_2024.pdf"), "w") as f:
            f.write("Colliding file")
        
        # Run normalization
        renamed_count = normalize_full_months_in_folder(self.test_dir)
        
        # Should only count the successful rename with the suffix
        self.assertEqual(renamed_count, 1)
        
        # Verify the files exist with correct names
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "doc_Jan_2024.pdf")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "doc_Jan_2024_1.pdf")))
        
        # Verify the contents were preserved
        with open(os.path.join(self.test_dir, "doc_Jan_2024.pdf"), "r") as f:
            self.assertEqual(f.read(), "Original file")
        with open(os.path.join(self.test_dir, "doc_Jan_2024_1.pdf"), "r") as f:
            self.assertEqual(f.read(), "Colliding file")

    def test_normalize_full_months_invalid_folder(self):
        """Test normalization with invalid folder path."""
        with self.assertRaises(ValidationError):
            normalize_full_months_in_folder("nonexistent_folder")

if __name__ == '__main__':
    unittest.main() 