"""
UI utility functions for creating consistent layouts across the batchRename application.
"""

import customtkinter as ctk
from typing import Callable
from .constants import (
    FONT_FAMILY, FONT_SIZE_NORMAL, FRAME_PADDING, TRANSPARENT_COLOR, HOVER_COLOR, TEXT_COLOR
)


def create_button(parent, text: str, command, width=None,
                  fg_color=None, hover_color=None, text_color=None) -> ctk.CTkButton:
    """
    Create a standardized button with common properties.
    
    Args:
        parent: Parent widget
        text: Button text
        command: Command to execute on click
        width: Optional button width
        fg_color: Optional foreground color
        hover_color: Optional hover color
        text_color: Optional text color
        
    Returns:
        ctk.CTkButton: The created button
    """
    kwargs = {
        "master": parent,
        "text": text,
        "command": command,
        "font": (FONT_FAMILY, FONT_SIZE_NORMAL)
    }

    # Only add optional parameters if they are not None
    if width is not None:
        kwargs["width"] = width
    if fg_color is not None:
        kwargs["fg_color"] = fg_color
    if hover_color is not None:
        kwargs["hover_color"] = hover_color
    else:
        kwargs["hover_color"] = HOVER_COLOR
    if text_color is not None:
        kwargs["text_color"] = text_color
    else:
        kwargs["text_color"] = TEXT_COLOR

    return ctk.CTkButton(**kwargs)


def create_standard_window_layout(parent, title: str, tool_name: str, back_command: Callable, 
                                content_frame: ctk.CTkFrame = None) -> tuple[ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel]:
    """
    Create a standardized window layout with back button, status label, and content area.
    
    Args:
        parent: Parent widget
        title: Window title
        tool_name: Name to display in status label
        back_command: Command to execute when back button is clicked
        content_frame: Optional content frame to use (if None, creates a new one)
        
    Returns:
        tuple: (content_frame, back_button, status_label)
    """
    # Create main content frame if not provided
    if content_frame is None:
        content_frame = ctk.CTkFrame(parent, fg_color=TRANSPARENT_COLOR)
        content_frame.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)
    
    # Create back button (bottom left)
    back_button = create_button(
        parent,
        text="← Back to Menu",
        command=back_command,
        width=100,
        fg_color="transparent",
        hover_color=("gray75", "gray25"),
        text_color=("gray50", "gray50")
    )
    back_button.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)
    
    # Create status label (bottom center)
    status_label = ctk.CTkLabel(
        parent,
        text=tool_name,
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        fg_color=("gray20", "gray20"),
        text_color=("gray70", "gray70"),
        corner_radius=5,
        width=150,
        height=30
    )
    status_label.place(relx=0.5, rely=1.0, anchor="s", x=0, y=-10)
    
    return content_frame, back_button, status_label


def create_standard_dialog_layout(parent, title: str, width: int = 400, height: int = 450) -> tuple[ctk.CTkToplevel, ctk.CTkFrame, ctk.CTkButton, ctk.CTkButton, ctk.CTkLabel]:
    """
    Create a standardized dialog layout with title, content area, and bottom buttons.
    
    Args:
        parent: Parent widget
        title: Dialog title
        width: Dialog width
        height: Dialog height
        
    Returns:
        tuple: (dialog, content_frame, back_button, save_button, status_label)
    """
    # Create dialog
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    # Main content frame
    main_frame = ctk.CTkFrame(dialog, fg_color=TRANSPARENT_COLOR)
    main_frame.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)
    
    # Content frame (leaves space for bottom elements)
    content_frame = ctk.CTkFrame(main_frame, fg_color=TRANSPARENT_COLOR)
    content_frame.pack(fill="both", expand=True, pady=(0, 50))
    
    # Back button (bottom left)
    back_button = create_button(
        dialog,
        text="← Back",
        command=lambda: dialog.destroy(),
        width=100,
        fg_color="transparent",
        hover_color=("gray75", "gray25"),
        text_color=("gray50", "gray50")
    )
    back_button.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)
    
    # Save button (bottom right)
    save_button = create_button(
        dialog,
        text="Save",
        command=lambda: dialog.destroy(),
        width=100
    )
    save_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    
    # Status label (bottom center)
    status_label = ctk.CTkLabel(
        dialog,
        text=title,
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        fg_color=("gray20", "gray20"),
        text_color=("gray70", "gray70"),
        corner_radius=5,
        width=150,
        height=30
    )
    status_label.place(relx=0.5, rely=1.0, anchor="s", x=0, y=-10)
    
    return dialog, content_frame, back_button, save_button, status_label


def create_standard_ui_row(parent, fg_color: str = TRANSPARENT_COLOR, 
                          padx: tuple = FRAME_PADDING, pady: tuple = (10, 5)) -> ctk.CTkFrame:
    """
    Create a standardized UI row frame that expands to fill its container.
    This is a flexible container for housing multiple elements like buttons, labels, text fields, etc.
    
    Args:
        parent: Parent widget
        fg_color: Background color for the row frame (default: transparent)
        padx: Horizontal padding (default: FRAME_PADDING)
        pady: Vertical padding (default: (10, 5))
        
    Returns:
        ctk.CTkFrame: A row frame that can be populated with any widgets
    """
    row_frame = ctk.CTkFrame(parent, fg_color=fg_color)
    row_frame.pack(fill="x", padx=padx, pady=pady)
    return row_frame


def create_text_frame(parent, fg_color: str = TRANSPARENT_COLOR) -> ctk.CTkFrame:
    """
    Create a text frame that expands to fill available space.
    This is commonly used for housing entry fields with buttons.
    
    Args:
        parent: Parent widget
        fg_color: Background color for the text frame (default: transparent)
        
    Returns:
        ctk.CTkFrame: A text frame that can be populated with entry fields and buttons
    """
    text_frame = ctk.CTkFrame(parent, fg_color=fg_color)
    text_frame.pack(side="left", fill="x", expand=True)
    return text_frame


def create_standard_form_field(parent, label_text: str, entry_width: int = 300, 
                             is_readonly: bool = False, initial_value: str = "") -> tuple[ctk.CTkLabel, ctk.CTkEntry]:
    """
    Create a standardized form field with label and entry.
    
    Args:
        parent: Parent widget
        label_text: Text for the label
        entry_width: Width of the entry field
        is_readonly: Whether the entry should be readonly
        initial_value: Initial value for the entry
        
    Returns:
        tuple: (label, entry)
    """
    # Label
    label = ctk.CTkLabel(parent, text=label_text)
    label.pack(anchor="w", pady=(0, 5))
    
    # Entry
    entry = ctk.CTkEntry(parent, width=entry_width)
    if is_readonly:
        entry.configure(state="readonly")
    if initial_value:
        entry.insert(0, initial_value)
    entry.pack(fill="x", pady=(0, 20))
    
    return label, entry


def create_standard_switch_field(parent, label_text: str, initial_value: bool = False) -> tuple[ctk.CTkLabel, ctk.CTkSwitch, ctk.BooleanVar]:
    """
    Create a standardized switch field with label and switch.
    
    Args:
        parent: Parent widget
        label_text: Text for the label
        initial_value: Initial value for the switch
        
    Returns:
        tuple: (label, switch, switch_var)
    """
    # Container frame for label and switch
    switch_frame = ctk.CTkFrame(parent, fg_color=TRANSPARENT_COLOR)
    switch_frame.pack(fill="x", pady=(0, 20))
    
    # Label on the left
    label = ctk.CTkLabel(
        switch_frame,
        text=label_text,
        font=(FONT_FAMILY, FONT_SIZE_NORMAL)
    )
    label.pack(side="left")
    
    # Switch on the right
    switch_var = ctk.BooleanVar(value=initial_value)
    switch = ctk.CTkSwitch(
        switch_frame,
        text="",  # No text on switch since we have a separate label
        variable=switch_var
    )
    switch.pack(side="right")
    
    return label, switch, switch_var


def create_inline_form_field(parent, label_text: str, entry_width: int = 200, 
                           is_readonly: bool = False, initial_value: str = "") -> tuple[ctk.CTkLabel, ctk.CTkEntry]:
    """
    Create a form field with label inline to the left of the entry field.
    
    Args:
        parent: Parent widget
        label_text: Text for the label
        entry_width: Width of the entry field
        is_readonly: Whether the entry should be readonly
        initial_value: Initial value for the entry
        
    Returns:
        tuple: (label, entry)
    """
    # Container frame for label and entry
    field_frame = ctk.CTkFrame(parent, fg_color=TRANSPARENT_COLOR)
    field_frame.pack(fill="x", pady=(0, 20))
    
    # Label on the left
    label = ctk.CTkLabel(
        field_frame,
        text=label_text,
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        width=100,
        anchor="w"
    )
    label.pack(side="left", padx=(0, 10))
    
    # Entry on the right
    entry = ctk.CTkEntry(field_frame, width=entry_width)
    if is_readonly:
        entry.configure(state="readonly")
    if initial_value:
        entry.insert(0, initial_value)
    entry.pack(side="left", fill="x", expand=True)
    
    return label, entry


def create_inline_label_field(parent, label_text: str, value_text: str = "") -> tuple[ctk.CTkLabel, ctk.CTkLabel]:
    """
    Create a field with label inline to the left and a value label on the right.
    
    Args:
        parent: Parent widget
        label_text: Text for the label
        value_text: Text to display as the value
        
    Returns:
        tuple: (label, value_label)
    """
    # Container frame for label and value
    field_frame = ctk.CTkFrame(parent, fg_color=TRANSPARENT_COLOR)
    field_frame.pack(fill="x", pady=(0, 20))
    
    # Label on the left
    label = ctk.CTkLabel(
        field_frame,
        text=label_text,
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        width=100,
        anchor="w"
    )
    label.pack(side="left", padx=(0, 10))
    
    # Value label on the right
    value_label = ctk.CTkLabel(
        field_frame,
        text=value_text,
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        fg_color=("gray20", "gray20"),
        text_color=("gray70", "gray70"),
        corner_radius=3,
        height=30
    )
    value_label.pack(side="left", fill="x", expand=True)
    
    return label, value_label