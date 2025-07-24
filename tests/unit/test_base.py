import unittest
import customtkinter as ctk
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock

class MessageboxPatchedTestCase(unittest.TestCase):
    """Base test case class that patches tkinter.messagebox globally."""
    
    def setUp(self):
        """Set up each test."""
        super().setUp()  # Call parent class setup first
        
        # Create a new mock for each test
        self.messagebox_patcher = patch('batch_renamer.tools.pdf_unlock.pdf_unlock_helper.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
        
        # Set up mock methods for messagebox
        self.mock_messagebox.showinfo = MagicMock()
        self.mock_messagebox.showwarning = MagicMock()
        self.mock_messagebox.showerror = MagicMock()
        self.mock_messagebox.askyesno = MagicMock()
        
        if hasattr(self, 'root') and self.root:
            self.root.update()

    def tearDown(self):
        """Clean up after each test."""
        # Stop the mock
        self.messagebox_patcher.stop()
        
        if hasattr(self, 'root') and self.root:
            try:
                self.root.update()
            except Exception:
                pass  # Ignore update errors during cleanup

class TkinterTestCase(unittest.TestCase):
    """Base test case class that provides a Tkinter root window."""
    
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for test files
        cls.test_dir = tempfile.mkdtemp()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory
        shutil.rmtree(cls.test_dir)
        super().tearDownClass()

    def setUp(self):
        """Set up each test."""
        # Mock the CTk class to avoid Tkinter initialization issues
        self.ctk_patcher = patch('customtkinter.CTk')
        self.mock_ctk = self.ctk_patcher.start()
        
        # Create a mock root window
        self.root = MagicMock()
        self.mock_ctk.return_value = self.root
        
        # Set up basic mock methods
        self.root.update = MagicMock()
        self.root.destroy = MagicMock()
        self.root.winfo_ismapped = MagicMock(return_value=True)
        self.root.cget = MagicMock(return_value="")
        self.root.master = None

    def tearDown(self):
        """Clean up after each test."""
        # Stop the mock
        self.ctk_patcher.stop()
        
        if hasattr(self, 'root') and self.root:
            try:
                self.root.destroy()
            except Exception:
                pass  # Ignore destroy errors during cleanup 