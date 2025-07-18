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
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / "backups"
        self.backup_dir.mkdir()
        
        # Create a test folder to backup
        self.source_dir = Path(self.test_dir) / "source"
        self.source_dir.mkdir()
        (self.source_dir / "test.txt").write_text("test content")
        
        # Mock the backup directory path
        self.backup_dir_patcher = patch('batch_renamer.backup_logic.get_backup_directory')
        self.mock_get_backup_dir = self.backup_dir_patcher.start()
        self.mock_get_backup_dir.return_value = self.backup_dir

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
        self.backup_dir_patcher.stop()

    @patch('batch_renamer.backup_logic.messagebox')
    def test_create_backup_interactive_success(self, mock_messagebox):
        # Test successful backup creation
        create_backup_interactive(str(self.source_dir))
        
        # Verify backup was created
        backup_files = list(self.backup_dir.glob(f"{BACKUP_PREFIX}*{BACKUP_EXTENSION}"))
        self.assertEqual(len(backup_files), 1)
        
        # Verify success message was shown
        mock_messagebox.showinfo.assert_called_once()
        
    @patch('batch_renamer.backup_logic.messagebox')
    def test_create_backup_interactive_invalid_folder(self, mock_messagebox):
        # Test with invalid folder
        create_backup_interactive("nonexistent_folder")
        
        # Verify error message was shown
        mock_messagebox.showerror.assert_called_once()
        
    @patch('batch_renamer.backup_logic.messagebox')
    @patch('batch_renamer.backup_logic.subprocess.run')
    def test_create_backup_interactive_overwrite(self, mock_run, mock_messagebox):
        # Create an initial backup
        backup_path = self.backup_dir / f"{BACKUP_PREFIX}source{BACKUP_EXTENSION}"
        backup_path.touch()
        
        # Mock successful 7z execution
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        
        # Mock user choosing to overwrite
        mock_messagebox.askyesno.return_value = True
        
        # Create new backup
        create_backup_interactive(str(self.source_dir))
        
        # Simulate 7z creating the backup file (since subprocess is mocked)
        if not backup_path.exists():
            backup_path.touch()
        
        # Verify old backup was deleted and new one created
        self.assertTrue(backup_path.exists())
        backup_files = list(self.backup_dir.glob(f"{BACKUP_PREFIX}*{BACKUP_EXTENSION}"))
        self.assertEqual(len(backup_files), 1)
        
    @patch('batch_renamer.backup_logic.messagebox')
    def test_create_backup_interactive_no_overwrite(self, mock_messagebox):
        # Create an initial backup
        backup_path = self.backup_dir / f"{BACKUP_PREFIX}source{BACKUP_EXTENSION}"
        backup_path.touch()
        initial_size = backup_path.stat().st_size
        
        # Mock user choosing not to overwrite
        mock_messagebox.askyesno.return_value = False
        
        # Try to create new backup
        create_backup_interactive(str(self.source_dir))
        
        # Verify backup was not changed
        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.stat().st_size, initial_size)
        
    @patch('batch_renamer.backup_logic.subprocess.run')
    def test_create_folder_backup_success(self, mock_run):
        # Mock successful 7z execution
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")

        result = create_folder_backup(str(self.source_dir))
        
        # Verify backup path is correct
        expected_path = self.backup_dir / f"{BACKUP_PREFIX}source{BACKUP_EXTENSION}"
        self.assertEqual(result, str(expected_path))
        
        # Verify 7z was called correctly
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "7z")
        self.assertEqual(args[1], "a")
        self.assertEqual(args[2], str(expected_path))
        self.assertEqual(args[3], str(self.source_dir))
        self.assertEqual(args[4], "-r")

    @patch('batch_renamer.backup_logic.subprocess.run')
    def test_create_folder_backup_7z_not_found(self, mock_run):
        # Mock 7z not found
        mock_run.side_effect = FileNotFoundError()
        
        with self.assertRaises(BackupError) as cm:
            create_folder_backup(str(self.source_dir))
        
        self.assertIn("Could not find '7z' executable", str(cm.exception))

    @patch('batch_renamer.backup_logic.subprocess.run')
    def test_create_folder_backup_7z_failure(self, mock_run):
        # Mock 7z failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "7z", stderr="Error")
        
        with self.assertRaises(BackupError) as cm:
            create_folder_backup(str(self.source_dir))
            
        self.assertIn("7z failed to create backup", str(cm.exception))

if __name__ == '__main__':
    unittest.main() 