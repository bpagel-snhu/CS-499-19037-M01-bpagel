# batch_renamer/ui/rename_options_frame.py

import customtkinter as ctk
from tkinter import messagebox
import os

from batch_renamer.rename_logic import (
    rename_files_in_folder,
    parse_filename_position_based,
    build_new_filename
)
from batch_renamer.logging_config import ui_logger as logger
from batch_renamer.exceptions import FileOperationError, ValidationError
from batch_renamer.constants import (
    FRAME_PADDING, GRID_PADDING, GRID_ROW_PADDING,
    PREFIX_ENTRY_WIDTH, PREVIEW_ENTRY_WIDTH, SLIDER_WIDTH
)
from batch_renamer.utils import create_button

from .month_normalize import count_full_months_in_folder, normalize_full_months_in_folder


class RenameOptionsFrame(ctk.CTkFrame):
    """
    A frame for date-based renaming using position-based parsing.
    Refactored to reduce repetitive widget and handler code.
    """

    def __init__(self, parent, main_window):
        super().__init__(parent)
        logger.info("Initializing RenameOptionsFrame")
        self.parent = parent
        self.main_window = main_window  # Main window reference
        self.manager = main_window.manager  # Get the FolderFileManager instance

        # Initialize variables
        self.prefix_var = ctk.StringVar(value="")
        self.preview_var = ctk.StringVar(value="")  # Start with empty preview
        self.month_textual_var = ctk.BooleanVar(value=False)
        self.day_enable_var = ctk.BooleanVar(value=False)

        self.year_start = 0
        self.year_length = 4
        self.month_start = 4
        self.month_length = 2
        self.day_start = 6
        self.day_length = 2
        self.day_enabled = False
        self.month_textual = False

        # Initialize file information first
        self.sample_filename = ""
        self.file_length = 0
        if self.manager.file_name:
            self.sample_filename = self.manager.file_name
            self.file_length = len(os.path.splitext(self.sample_filename)[0])

        # Initialize labels and sliders
        self.year_substring_label = None
        self.month_substring_label = None
        self.day_substring_label = None

        self.year_slider = None
        self.month_slider = None
        self.day_slider = None

        # Create UI elements
        self._create_widgets()
        self._create_layout()

        # Update UI with file information
        if self.sample_filename:
            self._update_all_substring_labels()
            self._auto_update_preview()
        else:
            self.preview_var.set("")  # Ensure preview is empty if no file selected

        self._check_and_warn_length_mismatch()
        logger.info("RenameOptionsFrame initialization complete")

    def _create_widgets(self):
        """Create all UI widgets for the rename options frame."""
        logger.debug("Creating rename options widgets")

        # Main content frame that will expand
        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inner_frame.pack(fill="both", expand=True)

        # Create a container for all content except warning
        content_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # Add prefix row
        self._create_prefix_row(content_frame)

        # Create Grid Frame for Sliders
        self.slider_grid_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.slider_grid_frame.pack(fill="both", expand=True, pady=(10, 10))

        self._create_grid_slider_row(0, "Year:", "year_slider", "year_substring_label", self._on_year_slider_changed,
                                     required_length=self.year_length)
        self._create_grid_slider_row(1, "Month:", "month_slider", "month_substring_label",
                                     self._on_month_slider_changed, required_length=self.month_length,
                                     checkbox_factory=self._create_textual_checkbox)
        self._create_grid_slider_row(2, "Day:", "day_slider", "day_substring_label", self._on_day_slider_changed,
                                     required_length=self.day_length, checkbox_factory=self._create_day_enable_checkbox)

        # Initially hide Day slider and preview, but ensure they're grid-managed first
        self.day_slider.grid()
        self.day_substring_label.grid()
        self.day_slider.grid_remove()
        self.day_substring_label.grid_remove()

        # Add preview row
        self._create_preview_row(content_frame)

        # Create warning frame at the bottom
        warning_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        warning_frame.pack(side="bottom", fill="x", pady=(10, 0))
        warning_frame.pack_propagate(False)  # Prevent frame from shrinking

        self.warning_label = ctk.CTkLabel(warning_frame, text="", text_color="orange")
        self.warning_label.pack(expand=True)
        logger.debug("Rename options widgets created successfully")

    def _create_layout(self):
        """Layout the widgets created in _create_widgets."""
        logger.debug("Creating layout for rename options frame")

        # Configure grid weights for the slider grid
        self.slider_grid_frame.grid_columnconfigure(0, weight=0, minsize=100)  # Year / Month / Day
        self.slider_grid_frame.grid_columnconfigure(1, weight=1)  # Slider column
        self.slider_grid_frame.grid_columnconfigure(2, weight=0, minsize=100)  # Checkboxes
        self.slider_grid_frame.grid_columnconfigure(3, weight=0, minsize=100)  # Substring preview

        # Configure grid row weights to distribute space evenly
        for i in range(3):  # For Year, Month, Day rows
            self.slider_grid_frame.grid_rowconfigure(i, weight=1)

        # Update all substring labels
        self._update_all_substring_labels()

        # Update preview if we have a sample file
        if self.manager.file_name:
            self.sample_filename = self.manager.file_name
            self.file_length = len(os.path.splitext(self.sample_filename)[0])
            self._auto_update_preview()

        # Check for length mismatches
        self._check_and_warn_length_mismatch()
        logger.debug("Layout created successfully")

    def _create_prefix_row(self, parent):
        """Create the prefix input row."""
        logger.debug("Creating prefix row")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row, text="Prefix:").pack(side="left")
        self.prefix_entry = ctk.CTkEntry(row, textvariable=self.prefix_var, width=PREFIX_ENTRY_WIDTH)
        self.prefix_entry.pack(side="left", padx=(10, 0))
        self.prefix_entry.bind("<KeyRelease>", self._on_any_field_changed)

    def _create_grid_slider_row(self, row_idx, label_text, slider_attr, label_attr, on_change, required_length,
                                checkbox_factory=None):
        """Create a row in the slider grid with a label, slider, optional checkbox, and preview label."""
        logger.debug(f"Creating slider row for {label_text}")
        ctk.CTkLabel(self.slider_grid_frame, text=label_text).grid(row=row_idx, column=0, sticky="w",
                                                                   padx=(0, GRID_PADDING), pady=GRID_ROW_PADDING)

        # Calculate max steps based on file length
        max_steps = max(0, self.file_length - required_length)

        slider = ctk.CTkSlider(
            self.slider_grid_frame,
            from_=0,
            to=max_steps,
            number_of_steps=max_steps + 1,
            command=on_change,
            width=SLIDER_WIDTH
        )
        slider.grid(row=row_idx, column=1, sticky="ew", padx=(GRID_PADDING, GRID_PADDING), pady=GRID_ROW_PADDING)
        setattr(self, slider_attr, slider)

        if checkbox_factory:
            checkbox = checkbox_factory(self.slider_grid_frame)
            checkbox.grid(row=row_idx, column=2, sticky="e", padx=(GRID_PADDING, GRID_PADDING), pady=GRID_ROW_PADDING)

        label = ctk.CTkLabel(self.slider_grid_frame, text="[--]")
        label.grid(row=row_idx, column=3, sticky="e", pady=GRID_ROW_PADDING)
        setattr(self, label_attr, label)

    def _create_textual_checkbox(self, parent):
        """Create checkbox for toggling textual month names."""
        logger.debug("Creating textual month checkbox")
        return ctk.CTkCheckBox(
            master=parent,
            text="Textual?",
            variable=self.month_textual_var,
            command=self._on_month_textual_changed
        )

    def _create_day_enable_checkbox(self, parent):
        """Create checkbox for enabling day selection."""
        logger.debug("Creating day enable checkbox")
        return ctk.CTkCheckBox(
            master=parent,
            text="Enable?",
            variable=self.day_enable_var,
            command=self._on_day_enable_toggled
        )

    def _create_preview_row(self, parent):
        """Create the preview and rename button row."""
        logger.debug("Creating preview row")
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(20, 0))

        ctk.CTkLabel(row, text="Preview:").pack(side="left")

        self.preview_entry = ctk.CTkEntry(
            row, textvariable=self.preview_var, width=PREVIEW_ENTRY_WIDTH, state="readonly"
        )
        self.preview_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))

        create_button(row, text="Rename All Files", command=self._on_rename_all).pack(side="right")

    def _check_and_warn_length_mismatch(self):
        """Check if files in the folder have different lengths and show warning."""
        if not self.manager.full_folder_path or not self.manager.file_name:
            self.warning_label.configure(text="")
            return

        try:
            files = os.listdir(self.manager.full_folder_path)
            if not files:
                self.warning_label.configure(text="")
                return

            # Get the length of the current file
            current_length = len(os.path.splitext(self.manager.file_name)[0])
            mismatched_files = []

            for file in files:
                if file == self.manager.file_name:
                    continue
                file_length = len(os.path.splitext(file)[0])
                if file_length != current_length:
                    mismatched_files.append(file)

            if mismatched_files:
                warning_text = f"WARNING: {len(mismatched_files)} files have different lengths"
                self.warning_label.configure(text=warning_text)
            else:
                self.warning_label.configure(text="")
        except Exception as e:
            logger.error(f"Error checking file lengths: {e}")
            self.warning_label.configure(text="")

    def _on_any_field_changed(self, event=None):
        """Handle changes to any input field."""
        logger.debug("Input field changed, updating preview")
        self._auto_update_preview()

    def _handle_slider_change(self, attr_start, attr_length, slider, label_update):
        """Handle slider value changes with bounds checking."""
        start = int(slider.get())
        max_start = max(0, self.file_length - getattr(self, attr_length))
        start = min(start, max_start)
        slider.set(start)
        setattr(self, attr_start, start)
        label_update()
        logger.debug(f"Slider changed: {attr_start}={start}")
        self._auto_update_preview()

    def _on_year_slider_changed(self, value):
        """Handle year slider changes."""
        self._handle_slider_change('year_start', 'year_length', self.year_slider, self._update_year_label)

    def _on_month_slider_changed(self, value):
        """Handle month slider changes."""
        self._handle_slider_change('month_start', 'month_length', self.month_slider, self._update_month_label)

    def _on_day_slider_changed(self, value):
        """Handle day slider changes."""
        self._handle_slider_change('day_start', 'day_length', self.day_slider, self._update_day_label)

    def _on_month_textual_changed(self):
        """Handle changes to the textual month checkbox."""
        if self.month_textual_var.get():
            logger.info("Textual month mode enabled")
            folder = self.parent.parent.full_folder_path
            if folder:
                count = count_full_months_in_folder(folder)
                if count > 0 and messagebox.askyesno("Normalize?",
                                                     f"{count} file(s) have full month names. Normalize?"):
                    logger.info(f"Normalizing {count} files with full month names")
                    try:
                        renamed = normalize_full_months_in_folder(folder)
                        logger.info(f"Successfully normalized {renamed} files")
                        messagebox.showinfo("Done", f"Renamed {renamed} file(s).")
                        self.parent.parent.file_name = None
                        self.parent.parent.full_file_path = None
                        self.destroy()
                        messagebox.showinfo("Reselect Sample File", "Please re-select sample file.")
                        return
                    except Exception as e:
                        logger.error(f"Failed to normalize month names: {str(e)}", exc_info=True)
                        messagebox.showerror("Error", f"Failed to normalize month names: {str(e)}")
                        self.month_textual_var.set(False)
                        return
            self.month_length = 3
        else:
            logger.info("Textual month mode disabled")
            self.month_length = 2
        self._auto_update_preview()

    def _on_day_enable_toggled(self):
        """Handle toggling of day enable checkbox."""
        logger.debug("Day enable toggled")
        self.day_enabled = self.day_enable_var.get()

        if self.day_enabled:
            self.day_slider.grid()
            self.day_substring_label.grid()
        else:
            self.day_slider.grid_remove()
            self.day_substring_label.grid_remove()

        self._auto_update_preview()

    def _update_label(self, start_attr, length_attr, label_widget):
        """Update a substring label with the current selection."""
        if not self.sample_filename:
            logger.warning("Cannot update label: no sample filename")
            return
        start = getattr(self, start_attr)
        length = getattr(self, length_attr)
        filename = os.path.splitext(self.sample_filename)[0]
        if start + length <= len(filename):
            substring = filename[start:start + length]
            label_widget.configure(text=f"[{substring}]")
            logger.debug(f"Label updated: {start_attr}={start}, {length_attr}={length}, substring={substring}")
        else:
            label_widget.configure(text="[--]")
            logger.warning(f"Label update failed: start={start}, length={length}, filename_length={len(filename)}")

    def _update_year_label(self):
        """Update the year substring label."""
        self._update_label('year_start', 'year_length', self.year_substring_label)

    def _update_month_label(self):
        """Update the month substring label."""
        self._update_label('month_start', 'month_length', self.month_substring_label)

    def _update_day_label(self):
        """Update the day substring label."""
        self._update_label('day_start', 'day_length', self.day_substring_label)

    def _update_all_substring_labels(self):
        """Update all substring labels."""
        logger.debug("Updating all substring labels")
        self._update_year_label()
        self._update_month_label()
        self._update_day_label()

    def _auto_update_preview(self):
        """Update the preview text based on current settings."""
        if not self.sample_filename:
            logger.warning("Cannot update preview: no sample filename")
            return

        try:
            filename = os.path.splitext(self.sample_filename)[0]
            extension = os.path.splitext(self.sample_filename)[1]

            # Parse date components
            date_info = parse_filename_position_based(
                filename,
                year_start=self.year_start,
                year_length=self.year_length,
                month_start=self.month_start,
                month_length=self.month_length,
                day_start=self.day_start if self.day_enabled else None,
                day_length=self.day_length if self.day_enabled else None,
                textual_month=self.month_textual_var.get()
            )

            # Build new filename
            year, month, day = date_info
            new_filename = build_new_filename(
                prefix=self.prefix_var.get(),
                year=year,
                month=month,
                day=day
            )

            self.preview_var.set(new_filename)
            logger.debug(f"Preview updated: {new_filename}")

        except (FileOperationError, ValidationError) as e:
            logger.error(f"Preview update failed: {str(e)}", exc_info=True)
            self.preview_var.set(f"Error: {str(e)}")

    def _on_rename_all(self):
        """Handle rename all files button click."""
        if not self.manager.full_folder_path:
            messagebox.showerror("Error", "No folder selected")
            return

        try:
            position_args = {
                'year_start': self.year_start,
                'year_length': self.year_length,
                'month_start': self.month_start,
                'month_length': self.month_length,
                'day_start': self.day_start if self.day_enabled else None,
                'day_length': self.day_length if self.day_enabled else None
            }

            result = rename_files_in_folder(
                self.manager.full_folder_path,
                prefix=self.prefix_var.get(),
                position_args=position_args,
                textual_month=self.month_textual_var.get(),
                dry_run=False,
                expected_length=self.file_length
            )

            # Show results
            message = f"Renamed {result['successful']} files"
            if result['skipped']:
                message += f"\nSkipped {len(result['skipped'])} files"
            messagebox.showinfo("Rename Complete", message)

        except (ValidationError, FileOperationError) as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logger.exception("Unexpected error during rename")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
