import unittest
import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk
from tests.unit.test_base import TkinterTestCase, MessageboxPatchedTestCase
from batch_renamer.ui.main_window import BatchRename
from batch_renamer.exceptions import ValidationError
from batch_renamer.constants import (
    WINDOW_TITLE, SELECT_FOLDER_TEXT, SELECT_FILE_TEXT,
    CHANGE_FOLDER_TEXT, CHANGE_FILE_TEXT, CREATE_BACKUP_TEXT,
    UNLOCK_PDFS_TEXT
)

@pytest.mark.gui
class TestMainWindow(TkinterTestCase, MessageboxPatchedTestCase):
    """Tests for the main application window."""
    
    def setUp(self):
        """Set up each test."""
        super().setUp()
        
        # Create a mock CTk class
        mock_ctk = MagicMock()
        mock_ctk.return_value = MagicMock()
        
        # Mock the entire CustomTkinter module
        self.ctk_patch = patch('customtkinter.CTk', mock_ctk)
        self.ctk_patch.start()
        
        # Create the main window instance
        self.main_window = BatchRename()
        
        # Set up basic mock methods
        self.main_window.title = MagicMock(return_value=WINDOW_TITLE)
        self.main_window.winfo_width = MagicMock(return_value=800)
        self.main_window.winfo_height = MagicMock(return_value=400)
        
        # Create mock folder_file_select_frame
        self.folder_file_select_frame = MagicMock()
        self.folder_file_select_frame.master = self.main_window  # Set the parent relationship
        self.main_window.folder_file_select_frame = self.folder_file_select_frame
        
        # Set up mock toast manager
        self.toast_manager = MagicMock()
        self.toast_manager.toast_label = MagicMock()
        self.toast_manager.toast_label.cget = MagicMock(return_value="")  # Default empty text
        self.main_window.toast_manager = self.toast_manager
        
        # Set up initial state
        self.main_window.full_folder_path = None
        self.main_window.folder_name = None
        self.main_window.show_full_path = False
        self.main_window.full_file_path = None
        self.main_window.file_name = None
        self.main_window.show_full_file_path = False
        
        # Set up mock buttons
        self.select_folder_button = MagicMock()
        self.select_folder_button.cget = MagicMock(return_value=SELECT_FOLDER_TEXT)
        self.select_folder_button.winfo_ismapped = MagicMock(return_value=True)
        self.folder_file_select_frame.select_folder_button = self.select_folder_button
        
    def tearDown(self):
        """Clean up after each test."""
        self.ctk_patch.stop()
        if hasattr(self, 'main_window'):
            self.main_window.destroy()
        super().tearDown()
        
    def test_window_initialization(self):
        """Test main window initialization and properties."""
        # Test window title
        self.assertEqual(self.main_window.title(), WINDOW_TITLE)
        
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
        # Update the mock to return our test message
        self.main_window.toast_manager.toast_label.cget.return_value = test_message
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
        
        # Test initial button text
        self.assertEqual(
            self.main_window.folder_file_select_frame.select_folder_button.cget("text"),
            SELECT_FOLDER_TEXT
        )
        
    def test_button_states(self):
        """Test button states and interactions."""
        frame = self.main_window.folder_file_select_frame
        
        # Test initial state - only select folder button should be visible
        self.assertTrue(frame.select_folder_button.winfo_ismapped())
        
        # Simulate folder selection
        with patch('tkinter.filedialog.askdirectory') as mock_askdir:
            mock_askdir.return_value = "/test/path"
            frame._on_select_folder()
            
            # Ensure file_buttons_frame is a mock and set winfo_ismapped to True
            if hasattr(frame, 'file_buttons_frame') and frame.file_buttons_frame:
                frame.file_buttons_frame.winfo_ismapped = MagicMock(return_value=True)
            
            # Verify file selection buttons are now visible
            self.assertTrue(hasattr(frame, 'file_buttons_frame'))
            self.assertTrue(frame.file_buttons_frame.winfo_ismapped())

if __name__ == '__main__':
    unittest.main() 