import customtkinter as ctk
from ..constants import FRAME_PADDING, BUTTON_WIDTH, WINDOW_TITLE, GRID_PADDING
from ..utils import create_button
import os
from tkinter import messagebox
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
LOGO_FILENAME = 'RB Barron Pagel - No BG.png'
LOGO_PATH = os.path.join(ASSETS_DIR, LOGO_FILENAME)
PLACEHOLDER_TOAST_TEXT = "Coming soon!"

# Placeholder for build date, to be replaced at build time
def get_build_date():
    try:
        return __BUILD_DATE__  # This should be set at build/compile time
    except NameError:
        import datetime
        return datetime.datetime.now().strftime('%Y-%m-%d')

class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self._create_widgets()

    def _create_widgets(self):
        # Title card
        title_label = ctk.CTkLabel(self, text=WINDOW_TITLE, font=("Arial", 28, "bold"))
        title_label.pack(pady=(FRAME_PADDING, FRAME_PADDING // 2))

        # Subtitle or description
        subtitle_label = ctk.CTkLabel(self, text="Select a tool below", font=("Arial", 12))
        subtitle_label.pack(pady=(0, FRAME_PADDING))

        # Main vertical button stack
        stack_frame = ctk.CTkFrame(self, fg_color="transparent")
        stack_frame.pack(fill="both", expand=True)

        # Tool buttons (top of stack)
        create_button(
            stack_frame,
            text="Bulk Rename",
            command=self._on_bulk_rename,
            width=BUTTON_WIDTH
        ).pack(pady=(0, FRAME_PADDING // 2), side="top")
        create_button(
            stack_frame,
            text="Database Logging",
            command=self._on_database_logging,
            width=BUTTON_WIDTH
        ).pack(pady=(0, FRAME_PADDING // 2), side="top")
        create_button(
            stack_frame,
            text="Unlock PDFs",
            command=self._on_unlock_pdfs,
            width=BUTTON_WIDTH
        ).pack(pady=(0, FRAME_PADDING // 2), side="top")

        # About/Exit buttons
        about_btn = create_button(
            stack_frame,
            text="About",
            command=self._on_about,
            width=BUTTON_WIDTH,
            fg_color="transparent",
            hover_color=None,
            text_color=None
        )
        about_btn.pack(pady=(0, GRID_PADDING), side="top")
        exit_btn = create_button(
            stack_frame,
            text="Exit",
            command=self._on_exit,
            width=BUTTON_WIDTH,
            fg_color="transparent",
            hover_color=None,
            text_color=None
        )
        exit_btn.pack(pady=(0, FRAME_PADDING // 2), side="top")

        # Logo image (fixed to bottom left, always visible)
        try:
            pil_image = Image.open(LOGO_PATH)
            max_height = 80
            aspect = pil_image.width / pil_image.height
            display_height = max_height
            display_width = int(aspect * display_height)
            resized = pil_image.resize((display_width, display_height), Image.LANCZOS)
            logo_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(display_width, display_height))
            self.logo_label = ctk.CTkLabel(self, image=logo_img, text="", fg_color="transparent")
            self.logo_label.image = logo_img  # Prevent garbage collection
            self.logo_label.place(relx=0.0, rely=1.0, anchor="sw", x=GRID_PADDING, y=-GRID_PADDING)
        except Exception as e:
            self.logo_label = ctk.CTkLabel(self, text="[Logo]", fg_color="transparent")
            self.logo_label.place(relx=0.0, rely=1.0, anchor="sw", x=GRID_PADDING, y=-GRID_PADDING)

    def _on_bulk_rename(self):
        self.main_window.show_folder_file_select()

    def _on_database_logging(self):
        self.main_window.show_toast(PLACEHOLDER_TOAST_TEXT)

    def _on_unlock_pdfs(self):
        self.main_window.show_toast(PLACEHOLDER_TOAST_TEXT)

    def _on_exit(self):
        self.main_window.destroy()

    def _on_about(self):
        messagebox.showinfo("About", "BatchRename\nA tool for bulk renaming files and other utilities.\n\nDeveloped by Bryce Pagel for Barron Pagel, PLLC.") 