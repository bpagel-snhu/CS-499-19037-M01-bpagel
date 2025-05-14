import unittest
import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
from tests.unit.test_base import TkinterTestCase, MessageboxPatchedTestCase
from batch_renamer.ui.main_window import BatchRename
from batch_renamer.exceptions import ValidationError

@pytest.mark.gui
class TestMainWindow(TkinterTestCase, MessageboxPatchedTestCase):
    """Tests for the main application window."""
    
    def setUp(self):
        """Set up each test."""
        super().setUp()
        # Create the main window instance
        self.main_window = BatchRename()
        self.main_window.update()
        
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'main_window'):
            self.main_window.destroy()
        super().tearDown()
        
    def test_window_initialization(self):
        """Test main window initialization and properties."""
        # Test window title
        self.assertEqual(self.main_window.title(), "Bulk File Renamer")
        
        # Test window size
        self.assertGreater(self.main_window.winfo_width(), 0)
        self.assertGreater(self.main_window.winfo_height(), 0)
        
        # Test that main components exist
        self.assertIsNotNone(self.main_window.folder_file_select_frame)
        self.assertIsNotNone(self.main_window.toast_manager)
        
    def test_initial_state(self):
        """Test initial state of the main window."""
        # Test initial state variables
        self.assertIsNone(self.main_window.full_folder_path)
        self.assertIsNone(self.main_window.folder_name)
        self.assertFalse(self.main_window.show_full_path)
        
        self.assertIsNone(self.main_window.full_file_path)
        self.assertIsNone(self.main_window.file_name)
        self.assertFalse(self.main_window.show_full_file_path)
        
    def test_toast_functionality(self):
        """Test toast message functionality."""
        test_message = "Test toast message"
        self.main_window.show_toast(test_message)
        
        # Verify toast label exists and has correct text
        self.assertIsNotNone(self.main_window.toast_manager.toast_label)
        self.assertEqual(self.main_window.toast_manager.toast_label.cget("text"), test_message)
        
    def test_folder_file_select_frame(self):
        """Test folder/file selection frame integration."""
        # Test that the frame is properly packed
        self.assertTrue(self.main_window.folder_file_select_frame.winfo_ismapped())
        
        # Test that the frame has the correct parent
        self.assertEqual(self.main_window.folder_file_select_frame.master, self.main_window)

if __name__ == '__main__':
    unittest.main() 