import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
from pathlib import Path
import pytest

from batch_renamer.ui.pdf_unlock_helper import unlock_pdfs_in_folder
from batch_renamer.exceptions import ValidationError, FileOperationError
from tests.unit.test_base import MessageboxPatchedTestCase

@pytest.mark.functional
class TestPDFUnlock(MessageboxPatchedTestCase):
    """Tests for PDF security removal functionality."""
    
    def setUp(self):
        super().setUp()
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
        super().tearDown()

    def test_unlock_pdfs_invalid_folder(self):
        """Test security removal with invalid folder path."""
        with self.assertRaises(ValidationError):
            unlock_pdfs_in_folder("nonexistent_folder")

    def test_unlock_pdfs_no_pdfs(self):
        """Test security removal in a folder with no PDF files."""
        # Create a folder with non-PDF files only
        for i in range(3):
            filename = f"test_{i}.txt"
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
        
        unlock_pdfs_in_folder(self.test_dir)
        self.mock_messagebox.showinfo.assert_called_once_with(
            "No PDFs Found",
            "There are no PDF files in the selected folder.",
            parent=None
        )

    @patch('pikepdf.open')
    def test_unlock_pdfs_success(self, mock_pdf_open):
        """Test successful PDF security removal."""
        # Create some test PDF files
        test_files = []
        for i in range(3):
            filename = f"test_{i}.pdf"
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(file_path)

        # Mock pikepdf to simulate successful security removal
        mock_pdf = MagicMock()
        mock_pdf.Root = MagicMock()
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Simulate user confirmation
        self.mock_messagebox.askyesno.return_value = True

        unlock_pdfs_in_folder(self.test_dir)

        # Verify messagebox calls
        self.assertEqual(self.mock_messagebox.askyesno.call_count, 1)
        self.mock_messagebox.askyesno.assert_any_call(
            "Confirm Security Removal",
            "Remove all security restrictions from 3 file(s)?\n\n"
            "This will remove digital signatures, edit restrictions, and other security features.",
            parent=None
        )
        self.mock_messagebox.showinfo.assert_called_once_with(
            "Security Removal Completed",
            "Removed security from 3 file(s) successfully.",
            parent=None
        )

        # Verify pikepdf was called for each file with correct security removal steps
        self.assertEqual(mock_pdf_open.call_count, 3)
        self.assertEqual(mock_pdf.remove_all_security.call_count, 3)
        self.assertEqual(mock_pdf.save.call_count, 3)
        
        # Verify each file was processed
        for file_path in test_files:
            mock_pdf_open.assert_any_call(file_path)
        
        # Verify the last save call had encryption disabled
        mock_pdf.save.assert_called_with(test_files[-1], encryption=False)

    @patch('pikepdf.open')
    def test_unlock_pdfs_with_permissions(self, mock_pdf_open):
        """Test security removal for PDFs with permissions and signatures."""
        # Create a test PDF file
        filename = "test_with_perms.pdf"
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w') as f:
            f.write("Test content")

        # Mock pikepdf with permissions
        mock_pdf = MagicMock()
        mock_pdf.Root = MagicMock()
        mock_pdf.Root.__contains__.side_effect = lambda x: x == '/Perms'
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Simulate user confirmation
        self.mock_messagebox.askyesno.return_value = True

        unlock_pdfs_in_folder(self.test_dir)

        # Verify permissions were removed
        self.assertEqual(mock_pdf.Root.__delitem__.call_count, 2)  # Called twice for /Perms
        mock_pdf.Root.__delitem__.assert_any_call('/Perms')

    @patch('pikepdf.open')
    def test_unlock_pdfs_user_cancelled(self, mock_pdf_open):
        """Test security removal when user cancels."""
        # Create some test PDF files
        test_files = []
        for i in range(3):
            filename = f"test_{i}.pdf"
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(file_path)

        # Simulate user cancellation
        self.mock_messagebox.askyesno.return_value = False

        unlock_pdfs_in_folder(self.test_dir)

        # Verify messagebox call
        self.assertEqual(self.mock_messagebox.askyesno.call_count, 1)
        self.mock_messagebox.askyesno.assert_any_call(
            "Confirm Security Removal",
            "Remove all security restrictions from 3 file(s)?\n\n"
            "This will remove digital signatures, edit restrictions, and other security features.",
            parent=None
        )

        # Verify pikepdf was not called
        mock_pdf_open.assert_not_called()

    @patch('pikepdf.open')
    def test_unlock_pdfs_error(self, mock_pdf_open):
        """Test security removal with errors."""
        # Create some test PDF files
        test_files = []
        for i in range(3):
            filename = f"test_{i}.pdf"
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(file_path)

        # Mock pikepdf to simulate errors
        mock_pdf_open.side_effect = [
            Exception("Test error 1"),  # First file fails with general error
            MagicMock().__enter__.return_value,  # Second file succeeds
            Exception("Test error 2")   # Third file fails with general error
        ]

        # Simulate user confirmation
        self.mock_messagebox.askyesno.return_value = True

        unlock_pdfs_in_folder(self.test_dir)

        # Verify messagebox calls
        self.mock_messagebox.askyesno.assert_called_once_with(
            "Confirm Security Removal",
            "Remove all security restrictions from 3 file(s)?\n\n"
            "This will remove digital signatures, edit restrictions, and other security features.",
            parent=None
        )
        self.mock_messagebox.showwarning.assert_called_once_with(
            "Security Removal Completed",
            "Removed security from 1 file(s) successfully.\n\nThe following files could not be processed:\ntest_0.pdf (error: Test error 1)\ntest_2.pdf (error: Test error 2)",
            parent=None
        )

if __name__ == '__main__':
    unittest.main() 