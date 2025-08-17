import unittest
import pytest
from unittest.mock import patch, MagicMock
from tests.unit.test_base import MessageboxPatchedTestCase
from batch_renamer.ui_utils import create_button


@pytest.mark.functional
class TestUIUtils(MessageboxPatchedTestCase):
    """Tests for UI utility functions."""
    
    def setUp(self):
        """Set up each test."""
        super().setUp()
        
    def test_create_button(self):
        """Test button creation utility."""
        # Create a mock parent
        mock_parent = MagicMock()
        test_text = "Test Button"
        test_command = MagicMock()
        
        # Mock the CTkButton class
        with patch('customtkinter.CTkButton') as mock_button_class:
            # Configure the mock button
            mock_button = MagicMock()
            mock_button_class.return_value = mock_button
            
            # Test button creation with default parameters
            button = create_button(mock_parent, test_text, test_command)
            
            # Verify button was created with correct parameters
            mock_button_class.assert_called_once_with(
                master=mock_parent,
                text=test_text,
                command=test_command,
                font=("Arial", 12),
                hover_color=("gray75", "gray25"),
                text_color=("gray10", "gray90")
            )
            
            # Test button creation with custom parameters
            mock_button_class.reset_mock()
            custom_button = create_button(
                mock_parent,
                test_text,
                test_command,
                width=100,
                fg_color="blue",
                hover_color="lightblue",
                text_color="white"
            )
            
            # Verify custom button was created with all parameters
            mock_button_class.assert_called_once_with(
                master=mock_parent,
                text=test_text,
                command=test_command,
                font=("Arial", 12),
                width=100,
                fg_color="blue",
                hover_color="lightblue",
                text_color="white"
            )
            
            # Test button creation with None parameters
            mock_button_class.reset_mock()
            none_button = create_button(
                mock_parent,
                test_text,
                test_command,
                width=None,
                fg_color=None,
                hover_color=None,
                text_color=None
            )
            
            # Verify that None parameters are not passed to the button
            mock_button_class.assert_called_once_with(
                master=mock_parent,
                text=test_text,
                command=test_command,
                font=("Arial", 12),
                hover_color=("gray75", "gray25"),
                text_color=("gray10", "gray90")
            )


if __name__ == '__main__':
    unittest.main() 