# UI Utility Functions

This document describes the utility functions available in `ui_utils.py` for creating consistent UI layouts across the batchRename application.

## Overview

The UI utility functions provide standardized layouts and components to ensure consistency across all tools and dialogs in the application. These functions establish the basic layout and foundational elements that can be easily populated and modified as necessary.

**Note:** UI utilities are now separated from general utilities. The `ui_utils.py` module contains all UI-related functions, while `utils.py` contains independent helper functions for file operations, config management, and system utilities.

## Available Functions

### 1. `create_standard_window_layout()`

Creates a standardized window layout with back button, status label, and content area. This is used for tool windows like PDF unlock, database logging, etc.

**Signature:**
```python
def create_standard_window_layout(parent, title: str, tool_name: str, back_command: Callable, 
                                content_frame: ctk.CTkFrame = None) -> tuple[ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel]
```

**Parameters:**
- `parent`: Parent widget
- `title`: Window title
- `tool_name`: Name to display in status label
- `back_command`: Command to execute when back button is clicked
- `content_frame`: Optional content frame to use (if None, creates a new one)

**Returns:**
- `content_frame`: The main content area for your tool
- `back_button`: The back button (bottom left)
- `status_label`: The status label (bottom center)

**Example Usage:**
```python
class MyToolFrame(ctk.CTkFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        
        # Use the standard window layout
        self.content_frame, self.back_button, self.status_label = create_standard_window_layout(
            parent=self,
            title="My Tool",
            tool_name="My Tool",
            back_command=self.main_window.show_main_menu
        )
        
        # Add your tool-specific content to self.content_frame
        self._create_tool_content()
```

### 2. `create_standard_dialog_layout()`

Creates a standardized dialog layout with title, content area, and bottom buttons. This is used for dialogs like edit_client_dialog.py.

**Signature:**
```python
def create_standard_dialog_layout(parent, title: str, width: int = 400, height: int = 450) -> tuple[ctk.CTkToplevel, ctk.CTkFrame, ctk.CTkButton, ctk.CTkButton, ctk.CTkLabel]
```

**Parameters:**
- `parent`: Parent widget
- `title`: Dialog title
- `width`: Dialog width (default: 400)
- `height`: Dialog height (default: 450)

**Returns:**
- `dialog`: The dialog window
- `content_frame`: The main content area
- `back_button`: The back button (bottom left)
- `save_button`: The save button (bottom right)
- `status_label`: The status label (bottom center)

**Example Usage:**
```python
class MyDialog:
    def __init__(self, parent):
        # Use the standard dialog layout
        self.dialog, self.content_frame, self.back_button, self.save_button, self.status_label = create_standard_dialog_layout(
            parent=parent,
            title="My Dialog",
            width=400,
            height=450
        )
        
        # Customize the save button command
        self.save_button.configure(command=self._on_save)
        
        # Add dialog-specific content
        self._create_dialog_content()
```

### 3. `create_standard_ui_row()`

Creates a standardized UI row frame that expands to fill its container. This is a flexible container for housing multiple elements like buttons, labels, text fields, etc.

**Signature:**
```python
def create_standard_ui_row(parent, fg_color: str = TRANSPARENT_COLOR, 
                          padx: tuple = FRAME_PADDING, pady: tuple = (10, 5)) -> ctk.CTkFrame
```

**Parameters:**
- `parent`: Parent widget
- `fg_color`: Background color for the row frame (default: transparent)
- `padx`: Horizontal padding (default: FRAME_PADDING)
- `pady`: Vertical padding (default: (10, 5))

**Returns:**
- `ctk.CTkFrame`: A row frame that can be populated with any widgets

**Example Usage:**
```python
# Create a simple row with label and entry
prefix_row = create_standard_ui_row(parent=self.content_frame, pady=(0, 10))
ctk.CTkLabel(prefix_row, text="Prefix:").pack(side="left")
self.prefix_entry = ctk.CTkEntry(prefix_row, width=200)
self.prefix_entry.pack(side="left", padx=(10, 0))

# Create a complex row with multiple elements
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
folder_button = create_button(folder_text_frame, text="📂", width=30, command=self._open_folder)
folder_button.pack(side="left")
self.folder_entry = ctk.CTkEntry(folder_text_frame, state="readonly")
self.folder_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

# Add action buttons
change_button = create_button(folder_row, text="Change Path", command=self._change_folder, width=90)
change_button.pack(side="left", padx=(10, 0))
```

### 4. `create_text_frame()`

Creates a text frame that expands to fill available space. This is commonly used for housing entry fields with buttons.

**Signature:**
```python
def create_text_frame(parent, fg_color: str = TRANSPARENT_COLOR) -> ctk.CTkFrame
```

**Parameters:**
- `parent`: Parent widget
- `fg_color`: Background color for the text frame (default: transparent)

**Returns:**
- `ctk.CTkFrame`: A text frame that can be populated with entry fields and buttons

**Example Usage:**
```python
# Create a text frame for entry and button
text_frame = create_text_frame(row_frame)
folder_button = create_button(text_frame, text="📂", width=30, command=self._open_folder)
folder_button.pack(side="left")
entry = ctk.CTkEntry(text_frame, state="readonly")
entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
```

### 5. `create_standard_form_field()`

Creates a standardized form field with label and entry.

**Signature:**
```python
def create_standard_form_field(parent, label_text: str, entry_width: int = 300, 
                             is_readonly: bool = False, initial_value: str = "") -> tuple[ctk.CTkLabel, ctk.CTkEntry]
```

**Parameters:**
- `parent`: Parent widget
- `label_text`: Text for the label
- `entry_width`: Width of the entry field (default: 300)
- `is_readonly`: Whether the entry should be readonly (default: False)
- `initial_value`: Initial value for the entry (default: "")

**Returns:**
- `tuple`: (label, entry)

**Example Usage:**
```python
# Create a regular form field
self.name_label, self.name_entry = create_standard_form_field(
    parent=self.content_frame,
    label_text="Name:",
    initial_value="John Doe"
)

# Create a readonly form field
self.created_label, self.created_entry = create_standard_form_field(
    parent=self.content_frame,
    label_text="Created:",
    is_readonly=True,
    initial_value="2024-01-01 12:00:00"
)
```

### 6. `create_standard_switch_field()`

Creates a standardized switch field with label and switch.

**Signature:**
```python
def create_standard_switch_field(parent, label_text: str, initial_value: bool = False) -> tuple[ctk.CTkLabel, ctk.CTkSwitch, ctk.BooleanVar]
```

**Parameters:**
- `parent`: Parent widget
- `label_text`: Text for the label
- `initial_value`: Initial value for the switch (default: False)

**Returns:**
- `tuple`: (label, switch, switch_var)

**Example Usage:**
```python
# Create a switch field
self.switch_label, self.switch, self.switch_var = create_standard_switch_field(
    parent=self.content_frame,
    label_text="Enable Feature:",
    initial_value=True
)

# Get the switch value
is_enabled = self.switch_var.get()
```

## Importing UI Utilities

To use the UI utility functions, import them from the `ui_utils` module:

```python
from batch_renamer.ui_utils import (
    create_standard_window_layout,
    create_standard_dialog_layout,
    create_standard_ui_row,
    create_text_frame,
    create_standard_form_field,
    create_standard_switch_field,
    create_button
)
```

## Integration with Main Window

To integrate a new tool with the main window, add a method like this to your main window class:

```python
def show_my_tool(self):
    if self.current_frame:
        self.current_frame.pack_forget()
        self.current_frame.destroy()
    self.current_frame = MyToolFrame(parent=self, main_window=self)
    self.current_frame.pack(padx=FRAME_PADDING, pady=FRAME_PADDING, fill="both", expand=True)
    self._hide_build_date_label()
    self._show_back_button()
    self._show_status_label("My Tool")
```

## Best Practices

1. **Use the utility functions**: Always use these utility functions for new tools and dialogs to maintain consistency.

2. **Customize as needed**: The utility functions provide sensible defaults, but you can customize them by modifying the returned widgets.

3. **Follow the patterns**: Study the existing tools (like PDF unlock, database logging) to understand how to structure your tool-specific content.

4. **Keep content in content_frame**: Add all your tool-specific widgets to the content_frame returned by the utility functions.

5. **Use the widget dictionaries**: The `create_standard_ui_row()` function returns a dictionary of widgets - use this to access and modify the widgets as needed.

## Examples

See `ui_examples.py` for complete examples of how to use these utility functions to create new tools and dialogs.

## Migration Guide

If you have existing tools that don't use these utilities, you can migrate them by:

1. Replacing manual layout code with calls to the utility functions
2. Moving tool-specific content into the content_frame
3. Using the standardized buttons and labels instead of custom ones

This will ensure consistency across all tools in the application. 