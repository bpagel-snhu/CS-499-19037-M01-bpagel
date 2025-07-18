# batch_renamer/ui/toast_manager.py

import customtkinter as ctk
from ..logging_config import ui_logger as logger

class ToastManager:
    """
    Handles showing temporary toast messages in the window.
    """
    def __init__(self, parent_window):
        logger.debug("Initializing ToastManager")
        self.parent = parent_window
        self.toast_label = None
        self._toast_after_id = None
        logger.debug("ToastManager initialization complete")

    def show_toast(self, message: str):
        """
        Displays a toast-like label and destroys any prior toast/timer first.
        
        Args:
            message: The message to display in the toast
        """
        logger.debug(f"Showing toast message: {message}")
        # Cancel old timer if it exists
        if self._toast_after_id is not None:
            logger.debug("Cancelling existing toast timer")
            self.parent.after_cancel(self._toast_after_id)
            self._toast_after_id = None

        # Destroy old label
        if self.toast_label is not None:
            logger.debug("Destroying existing toast label")
            self.toast_label.destroy()
            self.toast_label = None

        # Create new toast label
        logger.debug("Creating new toast label")
        self.toast_label = ctk.CTkLabel(
            self.parent,
            text=message,
            fg_color="gray40",
            corner_radius=5,
            text_color="white",
            padx=10,
            pady=5
        )
        # Position near bottom-left
        self.toast_label.place(
            relx=0.0,
            rely=1.0,
            anchor="sw",
            x=30,
            y=-30
        )

        # Schedule destruction
        logger.debug("Scheduling toast destruction")
        self._toast_after_id = self.parent.after(10_000, self._destroy_toast)

    def _destroy_toast(self):
        """Destroy the toast label and clear the timer."""
        logger.debug("Destroying toast")
        if self.toast_label:
            self.toast_label.destroy()
            self.toast_label = None
        self._toast_after_id = None
