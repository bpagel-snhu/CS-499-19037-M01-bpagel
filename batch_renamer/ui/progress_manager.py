# batch_renamer/ui/progress_manager.py

import customtkinter as ctk
import threading
import time
from typing import Callable, Optional, Any
from ..logging_config import ui_logger as logger
from ..constants import FONT_FAMILY, FONT_SIZE_NORMAL, FRAME_PADDING

class ProgressWindow(ctk.CTkToplevel):
    """
    A dedicated window for displaying progress bars.
    This prevents layout conflicts with the main application window.
    """
    
    def __init__(self, parent_window, title: str = "Processing...", determinate: bool = True, can_cancel: bool = True):
        super().__init__(parent_window)
        
        # Configure the progress window
        self.title(title)
        self.geometry("500x200")
        self.resizable(False, False)
        
        # Make it modal (user must interact with it before returning to main window)
        self.transient(parent_window)
        self.grab_set()
        
        # Center the window on the parent
        self.center_on_parent(parent_window)
        
        # Progress state
        self._cancelled = False
        
        # Create UI elements
        self._create_widgets(title, determinate, can_cancel)
        
        # Set focus to this window
        self.focus_set()
        
        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def center_on_parent(self, parent_window):
        """Center this window on the parent window."""
        # Get parent window position and size
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        
        # Get this window's size
        self.update_idletasks()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        # Ensure window is on screen
        x = max(0, x)
        y = max(0, y)
        
        self.geometry(f"+{x}+{y}")
        
    def _create_widgets(self, title: str, determinate: bool, can_cancel: bool):
        """Create the progress window widgets."""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title label
        self._progress_label = ctk.CTkLabel(
            main_frame,
            text=title,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL + 2),
            text_color="white"
        )
        self._progress_label.pack(pady=(20, 10))
        
        # Progress bar
        self._progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=400,
            height=25,
            progress_color="#4caf50",  # Light Green
            fg_color="gray30"
        )
        self._progress_bar.pack(pady=(0, 20))
        
        if determinate:
            self._progress_bar.set(0.0)
        else:
            self._progress_bar.set(0.0)
            self._start_indeterminate_animation()
        
        # Cancel button (optional)
        if can_cancel:
            self._cancel_button = ctk.CTkButton(
                main_frame,
                text="Cancel",
                width=120,
                height=35,
                fg_color="#f44336",  # Red
                hover_color="#d32f2f",
                command=self._on_cancel
            )
            self._cancel_button.pack(pady=(0, 10))
        else:
            self._cancel_button = None
            
    def update_progress(self, value: float, message: Optional[str] = None) -> None:
        """
        Update the progress bar value and optionally the message.
        
        Args:
            value: Progress value between 0.0 and 1.0
            message: Optional message to update the label with
        """
        if not self._progress_bar:
            return
            
        # Ensure value is between 0 and 1
        value = max(0.0, min(1.0, value))
        
        self._progress_bar.set(value)
        
        if message and self._progress_label:
            self._progress_label.configure(text=message)
            
        # Force update to show progress
        self.update_idletasks()
        
    def update_message(self, message: str) -> None:
        """Update just the progress message."""
        if self._progress_label:
            self._progress_label.configure(text=message)
            self.update_idletasks()
            
    def is_cancelled(self) -> bool:
        """Check if the operation was cancelled."""
        return self._cancelled
        
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        logger.debug("Operation cancelled by user")
        self._cancelled = True
        if self._cancel_button:
            self._cancel_button.configure(text="Cancelling...", state="disabled")
            
    def _on_close(self) -> None:
        """Handle window close event."""
        logger.debug("Progress window closed by user")
        self._cancelled = True
        self.destroy()
        
    def _start_indeterminate_animation(self) -> None:
        """Start indeterminate progress animation."""
        if not self._progress_bar:
            return
            
        def animate():
            if self._cancelled:
                return
                
            # Create a bouncing animation
            import math
            t = time.time() * 2  # Speed up animation
            value = (math.sin(t) + 1) / 2  # Convert to 0-1 range
            self._progress_bar.set(value)
            
            # Schedule next animation frame
            self.after(50, animate)
            
        animate()


class ProgressManager:
    """
    Manages progress bars for long-running operations.
    Now creates a dedicated progress window to prevent layout conflicts.
    Supports both determinate (with known total) and indeterminate progress.
    Can run operations in background threads to prevent UI freezing.
    """
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self._progress_window = None
        self._is_visible = False
        
    def show_progress(self, title: str = "Processing...", determinate: bool = True, 
                     can_cancel: bool = True) -> None:
        """
        Show a progress window with the given title.
        
        Args:
            title: The title to display above the progress bar
            determinate: Whether the progress bar should show actual progress (True) or indeterminate animation (False)
            can_cancel: Whether to show a cancel button
        """
        if self._is_visible:
            self.hide_progress()
            
        logger.debug(f"Showing progress window: {title}")
        
        # Create progress window
        self._progress_window = ProgressWindow(
            self.parent,
            title=title,
            determinate=determinate,
            can_cancel=can_cancel
        )
        
        self._is_visible = True
        
        # Force update to show the progress window
        self.parent.update_idletasks()
        
    def hide_progress(self) -> None:
        """Hide the progress window."""
        if self._is_visible and self._progress_window:
            logger.debug("Hiding progress window")
            try:
                self._progress_window.destroy()
            except:
                pass  # Window might already be destroyed
            self._progress_window = None
            self._is_visible = False
            
    def update_progress(self, value: float, message: Optional[str] = None) -> None:
        """
        Update the progress bar value and optionally the message.
        
        Args:
            value: Progress value between 0.0 and 1.0
            message: Optional message to update the label with
        """
        if self._is_visible and self._progress_window:
            self._progress_window.update_progress(value, message)
        
    def update_message(self, message: str) -> None:
        """Update just the progress message."""
        if self._is_visible and self._progress_window:
            self._progress_window.update_message(message)
            
    def is_cancelled(self) -> bool:
        """Check if the operation was cancelled."""
        if self._is_visible and self._progress_window:
            return self._progress_window.is_cancelled()
        return False
        
    def run_with_progress(self, operation: Callable, title: str = "Processing...", 
                         determinate: bool = True, can_cancel: bool = True) -> Any:
        """
        Run an operation with a progress window in a background thread.
        
        Args:
            operation: The function to run (should accept a progress_callback parameter)
            title: Title for the progress window
            determinate: Whether to show determinate progress
            can_cancel: Whether to show cancel button
            
        Returns:
            The result of the operation, or None if cancelled
        """
        result = [None]  # Use list to store result from thread
        exception = [None]  # Use list to store any exception
        
        def run_operation():
            try:
                # Pass a progress callback to the operation
                def progress_callback(value: float, message: Optional[str] = None):
                    if self.is_cancelled():
                        return False  # Signal to stop
                    self.update_progress(value, message)
                    return True  # Signal to continue
                    
                result[0] = operation(progress_callback)
            except Exception as e:
                exception[0] = e
                logger.error(f"Operation failed: {e}")
            finally:
                # Hide progress window when done
                self.parent.after(0, self.hide_progress)
        
        # Show progress window
        self.show_progress(title, determinate, can_cancel)
        
        # Run operation in background thread
        thread = threading.Thread(target=run_operation, daemon=True)
        thread.start()
        
        # Wait for completion or cancellation
        while thread.is_alive() and not self.is_cancelled():
            self.parent.update()  # Keep UI responsive
            time.sleep(0.01)  # Small delay to prevent busy waiting
            
        if exception[0]:
            raise exception[0]
            
        return result[0]
