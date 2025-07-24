# batch_renamer/ui/toast_manager.py

import customtkinter as ctk
from ..logging_config import ui_logger as logger

class ToastManager:
    """
    Handles showing temporary toast messages in the window.
    Now supports stacking multiple toasts.
    """
    TOAST_HEIGHT = 40  # px, approximate
    SPACING = 2        # px, space between toasts
    TOAST_DURATION = 5_000  # ms, how long the toast is visible
    ANIMATION_DURATION = 100 # ms, how long the wipe-left animation lasts
    ANIMATION_STEPS = 30     # number of steps in the wipe-left animation

    def __init__(self, parent_window):
        logger.debug("Initializing ToastManager")
        self.parent = parent_window
        self._toasts = []  # List of dicts: {"label": label, "after_id": after_id}
        logger.debug("ToastManager initialization complete")

    def show_toast(self, message: str):
        """
        Displays a toast-like label and stacks it above any existing toasts.
        Each toast expires independently.
        Now includes a thin progress bar at the bottom, inside a frame.
        """
        logger.debug(f"Showing toast message: {message}")
        # Calculate y offset based on number of active toasts
        base_y = -30
        y_offset = base_y - (len(self._toasts) * (self.TOAST_HEIGHT + self.SPACING))

        # Create a frame to hold the label and progress bar
        frame = ctk.CTkFrame(self.parent, fg_color="gray40", corner_radius=5)
        frame.place(
            relx=0.0,
            rely=1.0,
            anchor="sw",
            x=30,
            y=y_offset
        )
        # Create the label inside the frame
        label = ctk.CTkLabel(
            frame,
            text=message,
            fg_color="transparent",
            text_color="white",
            padx=10,
            pady=0
        )
        label.pack(fill="both", expand=True, side="top")
        frame.update_idletasks()
        frame_width = frame.winfo_width() or frame.winfo_reqwidth()
        # Add a thin progress bar at the bottom of the frame
        progress = ctk.CTkProgressBar(
            frame,
            height=3,
            width=frame_width,
            progress_color="#4caf50",  # Light Green
            fg_color="gray30",
            corner_radius=0
        )
        progress.pack(fill="x", side="bottom")
        progress.set(1.0)

        # Animate the progress bar
        duration = self.TOAST_DURATION - 300  # 300 ms buffer to ensure progress bar completes before wipe
        interval = duration // 100  # 100 steps for smoothness
        steps = duration // interval
        def animate(step=0):
            if step > steps:
                return
            progress.set(1.0 - step / steps)
            if step < steps:
                progress.after(interval, animate, step + 1)
        animate()

        # Schedule destruction
        after_id = self.parent.after(self.TOAST_DURATION, lambda: self._destroy_toast(frame))
        self._toasts.append({"frame": frame, "label": label, "progress": progress, "after_id": after_id})

        # Ensure geometry is realized and restack all toasts
        self.parent.update_idletasks()
        self._reposition_toasts()

    def _destroy_toast(self, frame):
        """Animate wipe left, then destroy the given toast frame and reposition remaining toasts."""
        logger.debug("Destroying toast (with wipe left animation)")
        # Find and remove from list
        idx = None
        for i, t in enumerate(self._toasts):
            if t["frame"] == frame:
                idx = i
                break
        if idx is not None:
            toast = self._toasts.pop(idx)
            # Cancel timer if still active
            if toast["after_id"] is not None:
                self.parent.after_cancel(toast["after_id"])
            # Animate wipe left
            start_x = frame.winfo_x()
            end_x = -frame.winfo_width() - 40  # Move fully off screen
            duration = self.ANIMATION_DURATION
            steps = self.ANIMATION_STEPS
            dx = (end_x - start_x) / steps
            interval = duration // steps
            def animate(step=0, x=start_x):
                if step >= steps:
                    frame.place_configure(x=end_x)
                    frame.destroy()
                    self._reposition_toasts()
                    return
                frame.place_configure(x=int(x))
                frame.after(interval, animate, step + 1, x + dx)
            animate()
        else:
            # If not found, just reposition
            self._reposition_toasts()

    def _reposition_toasts(self):
        base_y = -30
        for i, t in enumerate(self._toasts):
            y_offset = base_y - (i * (self.TOAST_HEIGHT + self.SPACING))
            t["frame"].place_configure(y=y_offset)
