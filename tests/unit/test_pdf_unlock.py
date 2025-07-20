import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
from pathlib import Path
import pytest

from batch_renamer.tools.pdf_unlock.pdf_unlock_helper import unlock_pdfs_in_folder
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
    @patch('pikepdf.Pdf.new')
    @patch('shutil.move')
    def test_unlock_pdfs_success(self, mock_move, mock_pdf_new, mock_pdf_open):
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
        mock_src_pdf = MagicMock()
        mock_src_pdf.pages = [MagicMock() for _ in range(3)]  # 3 pages per PDF
        mock_pdf_open.return_value.__enter__.return_value = mock_src_pdf

        mock_dst_pdf = MagicMock()
        mock_pdf_new.return_value.__enter__.return_value = mock_dst_pdf

        # Simulate user confirmation
        self.mock_messagebox.askyesno.return_value = True

        unlock_pdfs_in_folder(self.test_dir)

        # Verify messagebox calls
        self.assertEqual(self.mock_messagebox.askyesno.call_count, 1)
        self.mock_messagebox.askyesno.assert_any_call(
            "Confirm Security Removal",
            "Remove security restrictions from 3 file(s)?\n\n"
            "This will remove digital signatures, edit restrictions, and other security features. "
            "The document's visual quality and text recognition will be preserved.\n\n"
            "This cannot be undone.",
            parent=None
        )
        self.mock_messagebox.showinfo.assert_called_once_with(
            "Security Removal Completed",
            "Removed security from 3 file(s) successfully.",
            parent=None
        )

        # Verify pikepdf was called for each file
        self.assertEqual(mock_pdf_open.call_count, 3)
        self.assertEqual(mock_pdf_new.call_count, 3)
        self.assertEqual(mock_dst_pdf.save.call_count, 3)
        self.assertEqual(mock_move.call_count, 3)
        
        # Verify each file was processed correctly
        for file_path in test_files:
            mock_pdf_open.assert_any_call(file_path)
            mock_dst_pdf.pages.append.assert_any_call(mock_src_pdf.pages[0])
            mock_dst_pdf.save.assert_any_call(mock_move.call_args_list[test_files.index(file_path)][0][0])

    @patch('pikepdf.open')
    @patch('pikepdf.Pdf.new')
    @patch('shutil.move')
    def test_unlock_pdfs_with_encryption(self, mock_move, mock_pdf_new, mock_pdf_open):
        """Test security removal for encrypted PDFs."""
        # Create a test PDF file
        filename = "test_encrypted.pdf"
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w') as f:
            f.write("Test content")

        # Mock pikepdf with encryption
        mock_src_pdf = MagicMock()
        mock_src_pdf.pages = [MagicMock()]
        mock_pdf_open.return_value.__enter__.return_value = mock_src_pdf

        mock_dst_pdf = MagicMock()
        mock_pdf_new.return_value.__enter__.return_value = mock_dst_pdf

        # Simulate user confirmation
        self.mock_messagebox.askyesno.return_value = True

        unlock_pdfs_in_folder(self.test_dir)

        # Verify file was processed correctly
        mock_pdf_open.assert_called_once_with(file_path)
        mock_dst_pdf.pages.append.assert_called_once_with(mock_src_pdf.pages[0])
        mock_dst_pdf.save.assert_called_once_with(mock_move.call_args[0][0])
        mock_move.assert_called_once()

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
            "Remove security restrictions from 3 file(s)?\n\n"
            "This will remove digital signatures, edit restrictions, and other security features. "
            "The document's visual quality and text recognition will be preserved.\n\n"
            "This cannot be undone.",
            parent=None
        )

        # Verify pikepdf was not called
        mock_pdf_open.assert_not_called()

    @patch('pikepdf.open')
    @patch('pikepdf.Pdf.new')
    @patch('shutil.move')
    def test_unlock_pdfs_error(self, mock_move, mock_pdf_new, mock_pdf_open):
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
            "Remove security restrictions from 3 file(s)?\n\n"
            "This will remove digital signatures, edit restrictions, and other security features. "
            "The document's visual quality and text recognition will be preserved.\n\n"
            "This cannot be undone.",
            parent=None
        )
        self.mock_messagebox.showwarning.assert_called_once_with(
            "Security Removal Completed",
            "Removed security from 1 file(s) successfully.\n\nThe following files could not be processed:\ntest_0.pdf (error: Test error 1)\ntest_2.pdf (error: Test error 2)",
            parent=None
        )

if __name__ == '__main__':
    unittest.main() 