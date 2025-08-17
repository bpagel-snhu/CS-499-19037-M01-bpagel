"""
UI Examples - Demonstrates how to use the UI utility functions for consistent layouts.

This file shows examples of how to use the utility functions to create consistent UI layouts
across different parts of the application.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from ..ui_utils import (
    create_standard_window_layout,
    create_standard_dialog_layout,
    create_standard_ui_row,
    create_text_frame,
    create_standard_form_field,
    create_standard_switch_field,
    create_button
)
from ..constants import FRAME_PADDING, TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR


class ExampleToolFrame(ctk.CTkFrame):
    """
    Example of how to use create_standard_window_layout for a new tool.
    This demonstrates the pattern used by existing tools like PDF unlock, database logging, etc.
    """
    
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.parent = parent
        self.main_window = main_window
        
        # Use the standard window layout utility
        self.content_frame, self.back_button, self.status_label = create_standard_window_layout(
            parent=self,
            title="Example Tool",
            tool_name="Example Tool",
            back_command=self.main_window.show_main_menu
        )
        
        # Now add your tool-specific content to self.content_frame
        self._create_tool_content()
    
    def _create_tool_content(self):
        """Add tool-specific content to the content frame."""
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame, 
            text="Example Tool", 
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(FRAME_PADDING, FRAME_PADDING // 2))
        
        # Example: Create a standard UI row for a folder path (using the new flexible approach)
        folder_row = create_standard_ui_row(parent=self.content_frame)
        
        # Add header label
        header_label = ctk.CTkLabel(
            folder_row, 
            text="Folder:", 
            font=("Arial", 12, "bold"), 
            width=80, 
            anchor="w", 
            fg_color=TRANSPARENT_COLOR
        )
        header_label.pack(side="left", padx=(0, 5))
        
        # Add text frame for entry and folder button
        folder_text_frame = create_text_frame(folder_row)
        
        # Add folder button
        folder_button = create_button(
            folder_text_frame,
            text="📂",
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._open_folder
        )
        folder_button.pack(side="left")
        
        # Add entry field
        self.folder_entry = ctk.CTkEntry(folder_text_frame, state="readonly")
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Add action buttons
        change_button = create_button(
            folder_row,
            text="Change Path",
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR,
            command=self._change_folder,
            width=90
        )
        change_button.pack(side="left", padx=(10, 0))
        
        reset_button = create_button(
            folder_row,
            text="Reset Path",
            command=self._reset_folder,
            width=90
        )
        reset_button.pack(side="left", padx=(10, 0))
        
        clear_button = create_button(
            folder_row,
            text="🗑",
            command=self._clear_folder,
            width=30,
            fg_color=TRANSPARENT_COLOR,
            hover_color=HOVER_COLOR,
            text_color=TEXT_COLOR
        )
        clear_button.pack(side="left", padx=(10, 0))
        
        # Example: Create a simple row with just label and entry (like prefix row in rename_options)
        prefix_row = create_standard_ui_row(parent=self.content_frame, pady=(0, 10))
        ctk.CTkLabel(prefix_row, text="Prefix:").pack(side="left")
        self.prefix_entry = ctk.CTkEntry(prefix_row, width=200)
        self.prefix_entry.pack(side="left", padx=(10, 0))
        
        # Example: Create a row with buttons on the right (like folder/file headers)
        action_row = create_standard_ui_row(parent=self.content_frame)
        
        # Text frame on the left
        action_text_frame = create_text_frame(action_row)
        ctk.CTkLabel(action_text_frame, text="Action:").pack(side="left")
        self.action_entry = ctk.CTkEntry(action_text_frame, state="readonly")
        self.action_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Buttons on the right
        self.process_button = create_button(
            action_row,
            text="Process",
            command=self._process_files,
            width=100
        )
        self.process_button.pack(side="right", padx=(5, 0))
        
        self.clear_button = create_button(
            action_row,
            text="Clear",
            command=self._clear_all,
            width=80
        )
        self.clear_button.pack(side="right", padx=(5, 0))
        
        # Example: Create form fields
        self.name_label, self.name_entry = create_standard_form_field(
            parent=self.content_frame,
            label_text="Name:",
            initial_value="Example Name"
        )
        
        # Example: Create a switch field
        self.switch_label, self.switch, self.switch_var = create_standard_switch_field(
            parent=self.content_frame,
            label_text="Enable Feature:",
            initial_value=True
        )
        
        # Example: Add action buttons using the flexible row approach
        action_frame = create_standard_ui_row(parent=self.content_frame, pady=(20, 0))
        
        process_button = create_button(
            action_frame,
            text="Process Files",
            command=self._process_files,
            width=150
        )
        process_button.pack(side="left", padx=(0, 10))
        
        clear_button = create_button(
            action_frame,
            text="Clear All",
            command=self._clear_all,
            width=100
        )
        clear_button.pack(side="left")
    
    def _open_folder(self):
        """Example folder button command."""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.folder_entry.configure(state="readonly")
    
    def _change_folder(self):
        """Example change folder command."""
        self._open_folder()
    
    def _reset_folder(self):
        """Example reset folder command."""
        self.folder_entry.configure(state="normal")
        self.folder_entry.delete(0, "end")
        self.folder_entry.configure(state="readonly")
    
    def _clear_folder(self):
        """Example clear folder command."""
        self._reset_folder()
    
    def _process_files(self):
        """Example process files command."""
        messagebox.showinfo("Info", "Processing files...")
    
    def _clear_all(self):
        """Example clear all command."""
        self.name_entry.delete(0, "end")
        self.switch_var.set(False)
        self._reset_folder()


class ExampleDialog:
    """
    Example of how to use create_standard_dialog_layout for a new dialog.
    This demonstrates the pattern used by existing dialogs like edit_client_dialog.py.
    """
    
    def __init__(self, parent):
        # Use the standard dialog layout utility
        self.dialog, self.content_frame, self.back_button, self.save_button, self.status_label = create_standard_dialog_layout(
            parent=parent,
            title="Example Dialog",
            width=400,
            height=450
        )
        
        # Customize the save button command
        self.save_button.configure(command=self._on_save)
        
        # Add dialog-specific content
        self._create_dialog_content()
    
    def _create_dialog_content(self):
        """Add dialog-specific content to the content frame."""
        # Example: Create form fields
        self.first_name_label, self.first_name_entry = create_standard_form_field(
            parent=self.content_frame,
            label_text="First Name:",
            initial_value="John"
        )
        
        self.last_name_label, self.last_name_entry = create_standard_form_field(
            parent=self.content_frame,
            label_text="Last Name:",
            initial_value="Doe"
        )
        
        # Example: Create a switch field
        self.switch_label, self.switch, self.switch_var = create_standard_switch_field(
            parent=self.content_frame,
            label_text="Active:",
            initial_value=True
        )
        
        # Example: Create a readonly field
        self.created_label, self.created_entry = create_standard_form_field(
            parent=self.content_frame,
            label_text="Created:",
            is_readonly=True,
            initial_value="2024-01-01 12:00:00"
        )
    
    def _on_save(self):
        """Handle save button click."""
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        is_active = self.switch_var.get()
        
        # Process the data here
        print(f"Saved: {first_name} {last_name}, Active: {is_active}")
        
        # Close the dialog
        self.dialog.destroy()


def show_example_dialog(parent):
    """Helper function to show the example dialog."""
    ExampleDialog(parent)


# Example usage in a main window method:
"""
def show_example_tool(self):
    if self.current_frame:
        self.current_frame.pack_forget()
        self.current_frame.destroy()
    self.current_frame = ExampleToolFrame(parent=self, main_window=self)
    self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
    self._hide_build_date_label()
    self._show_back_button()
    self._show_status_label("Example Tool")
""" 