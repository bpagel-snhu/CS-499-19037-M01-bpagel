import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import pytest

from batch_renamer.backup_logic import (
    create_folder_backup,
    create_backup_interactive,
    BackupError,
    ValidationError
)
from batch_renamer.constants import BACKUP_PREFIX, BACKUP_EXTENSION

@pytest.mark.functional
class TestBackupLogic(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for test files and backups
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = tempfile.mkdtemp()
        
        # Create some test PDF files
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"test_file_{i}.pdf")
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            self.test_files.append(file_path)

        # Mock backup directory path
        patcher = patch('batch_renamer.backup_logic.get_backup_directory')
        self.mock_get_backup_dir = patcher.start()
        self.mock_get_backup_dir.return_value = Path(self.backup_dir)
        self.addCleanup(patcher.stop)

    def tearDown(self):
        # Clean up the temporary directories
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.backup_dir)

    @patch('subprocess.run')
    def test_create_folder_backup(self, mock_run):
        # Mock successful 7z execution
        mock_run.return_value = MagicMock(
            stdout="Everything is Ok",
            stderr="",
            returncode=0
        )

        # Test creating a backup
        backup_path = create_folder_backup(self.test_dir)
        
        # Verify 7z was called correctly
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "7z")
        self.assertEqual(args[1], "a")
        self.assertTrue(str(args[2]).endswith(".zip"))  # Backup file path
        self.assertEqual(args[3], self.test_dir)  # Source folder
        self.assertEqual(args[4], "-r")  # Recursive flag

    @patch('subprocess.run')
    def test_create_folder_backup_7z_not_found(self, mock_run):
        # Mock 7z not found
        mock_run.side_effect = FileNotFoundError("7z not found")
        
        with self.assertRaises(BackupError) as context:
            create_folder_backup(self.test_dir)
        
        self.assertIn("Could not find '7z' executable", str(context.exception))

    @patch('subprocess.run')
    def test_create_folder_backup_7z_error(self, mock_run):
        # Mock 7z error
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="7z",
            output="",
            stderr="Access denied"
        )
        
        with self.assertRaises(BackupError) as context:
            create_folder_backup(self.test_dir)
        
        self.assertIn("7z failed to create backup", str(context.exception))

    def test_create_folder_backup_invalid_folder(self):
        # Test with non-existent folder
        with self.assertRaises(ValidationError):
            create_folder_backup("nonexistent_folder")

    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    @patch('subprocess.run')
    def test_create_backup_interactive(self, mock_run, mock_error, mock_info, mock_askyesno):
        # Mock successful 7z execution
        mock_run.return_value = MagicMock(
            stdout="Everything is Ok",
            stderr="",
            returncode=0
        )
        
        # Test successful backup creation
        create_backup_interactive(self.test_dir)
        
        # Verify success message was shown
        mock_info.assert_called_once()
        self.assertIn("Successfully created backup", mock_info.call_args[0][1])

    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    @patch('subprocess.run')
    def test_create_backup_interactive_existing_backup(self, mock_run, mock_error, mock_info, mock_askyesno):
        # Create a dummy backup file
        folder_name = os.path.basename(self.test_dir)
        backup_path = os.path.join(self.backup_dir, f"{BACKUP_PREFIX}{folder_name}{BACKUP_EXTENSION}")
        with open(backup_path, 'w') as f:
            f.write("dummy backup")

        # Mock user choosing not to overwrite
        mock_askyesno.return_value = False
        
        # Test backup creation with existing file
        create_backup_interactive(self.test_dir)
        
        # Verify user was asked about overwrite
        mock_askyesno.assert_called_once()
        args = mock_askyesno.call_args[0]
        self.assertEqual(args[0], "Overwrite Existing Backup?")
        self.assertIn("A backup already exists:", args[1])
        self.assertIn(str(backup_path), args[1])
        self.assertIn("Overwrite it?", args[1])
        
        # Verify no backup was created
        mock_run.assert_not_called()

    @patch('tkinter.messagebox.showerror')
    def test_create_backup_interactive_invalid_folder(self, mock_error):
        # Test with invalid folder
        create_backup_interactive("nonexistent_folder")
        
        # Verify error message was shown
        mock_error.assert_called_once()
        self.assertIn("No valid folder selected", mock_error.call_args[0][1])

if __name__ == '__main__':
    unittest.main() 