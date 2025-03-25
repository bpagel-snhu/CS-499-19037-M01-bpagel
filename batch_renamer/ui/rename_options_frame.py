# batch_renamer/ui/rename_options_frame.py

import customtkinter as ctk
from tkinter import messagebox
import os

from batch_renamer.rename_logic import (
    rename_files_in_folder,
    parse_filename_position_based,
    build_new_filename
)

from .month_normalize import count_full_months_in_folder, normalize_full_months_in_folder

class RenameOptionsFrame(ctk.CTkFrame):
    """
    A frame for date-based renaming using position-based parsing.
    Refactored to reduce repetitive widget and handler code.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.prefix_var = ctk.StringVar(value="")
        self.preview_var = ctk.StringVar(value="")
        self.month_textual_var = ctk.BooleanVar(value=False)

        self.year_start = 0
        self.year_length = 4
        self.month_start = 0
        self.month_length = 2
        self.day_start = 0
        self.day_length = 2
        self.day_enabled = False

        self.file_length = len(os.path.splitext(self.parent.file_name)[0]) if self.parent.file_name else 0
        self.sample_filename = self.parent.file_name or ""

        self.year_substring_label = None
        self.month_substring_label = None
        self.day_substring_label = None

        self.year_slider = None
        self.month_slider = None
        self.day_slider = None

        self._create_widgets()
        self._update_all_substring_labels()
        self._auto_update_preview()

        self._check_and_warn_length_mismatch()

    def _create_widgets(self):
        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inner_frame.pack(padx=20, pady=20, fill="x")

        self._create_prefix_row()

        # Create Grid Frame for Sliders
        self.slider_grid_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        self.slider_grid_frame.pack(fill="x", pady=(10, 10))

        self._create_grid_slider_row(0, "Year:", "year_slider", "year_substring_label", self._on_year_slider_changed,
                                     required_length=self.year_length)
        self._create_grid_slider_row(1, "Month:", "month_slider", "month_substring_label",
                                     self._on_month_slider_changed, required_length=self.month_length,
                                     checkbox_factory=self._create_textual_checkbox)
        self._create_grid_slider_row(2, "Day:", "day_slider", "day_substring_label", self._on_day_slider_changed,
                                     required_length=self.day_length, checkbox_factory=self._create_day_enable_checkbox)

        # Initially hide Day slider and preview
        self.day_slider.grid_remove()
        self.day_substring_label.grid_remove()

        self._create_preview_row()

        self.warning_label = ctk.CTkLabel(self.inner_frame, text="", text_color="orange")
        self.warning_label.pack(pady=(10, 0))

    def _create_prefix_row(self):
        row = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row, text="Prefix:").pack(side="left")
        self.prefix_entry = ctk.CTkEntry(row, textvariable=self.prefix_var, width=200)
        self.prefix_entry.pack(side="left", padx=(10, 0))
        self.prefix_entry.bind("<KeyRelease>", self._on_any_field_changed)

    def _create_grid_slider_row(self, row_idx, label_text, slider_attr, label_attr, on_change, required_length,
                                checkbox_factory=None):
        ctk.CTkLabel(self.slider_grid_frame, text=label_text).grid(row=row_idx, column=0, sticky="w", padx=(0, 5))

        slider = ctk.CTkSlider(
            self.slider_grid_frame,
            from_=0,
            to=self.file_length - required_length,  # ✅ Prevents slider overshoot
            number_of_steps=(self.file_length - required_length + 1),
            command=on_change,
            width=250
        )
        slider.grid(row=row_idx, column=1, sticky="ew", padx=(5, 5))
        setattr(self, slider_attr, slider)

        if checkbox_factory:
            checkbox = checkbox_factory(self.slider_grid_frame)
            checkbox.grid(row=row_idx, column=2, sticky="e", padx=(5, 5))

        label = ctk.CTkLabel(self.slider_grid_frame, text="[--]")
        label.grid(row=row_idx, column=3, sticky="e")
        setattr(self, label_attr, label)

        self.slider_grid_frame.grid_columnconfigure(0, weight=0, minsize=100)  # Year / Month / Day
        self.slider_grid_frame.grid_columnconfigure(1, weight=1)  # Slider column
        self.slider_grid_frame.grid_columnconfigure(2, weight=0, minsize=100)  # Checkboxes
        self.slider_grid_frame.grid_columnconfigure(3, weight=0, minsize=100)  # Substring preview

    def _create_textual_checkbox(self, parent):
        # Explicit parent passed to avoid grid/pack conflict
        return ctk.CTkCheckBox(
            master=parent,
            text="Textual?",
            variable=self.month_textual_var,
            command=self._on_month_textual_changed
        )

    def _create_day_enable_checkbox(self, parent):
        self.day_enable_var = ctk.BooleanVar(value=False)
        return ctk.CTkCheckBox(
            master=parent,
            text="Enable?",
            variable=self.day_enable_var,
            command=self._on_day_enable_toggled
        )

    def _create_preview_row(self):
        row = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        row.pack(fill="x", pady=(20, 0))

        ctk.CTkLabel(row, text="Preview:").pack(side="left")

        self.preview_entry = ctk.CTkEntry(
            row, textvariable=self.preview_var, width=300, state="readonly"
        )
        self.preview_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))

        ctk.CTkButton(row, text="Rename All Files", command=self._on_rename_all).pack(side="right")

    def _check_and_warn_length_mismatch(self):
        if not self.parent.full_folder_path or not self.parent.file_name:
            return

        folder = self.parent.full_folder_path
        sample_len = len(self.parent.file_name)
        mismatch_count = sum(
            1 for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and len(f) != sample_len
        )

        if mismatch_count > 0:
            self.warning_label.configure(
                text=(
                    f"WARNING: {mismatch_count} out of {len(os.listdir(folder))} files have a different length."
                )
            )

    def _on_any_field_changed(self, event=None):
        self._auto_update_preview()

    def _handle_slider_change(self, attr_start, attr_length, slider, label_update):
        start = int(slider.get())
        max_start = max(0, self.file_length - getattr(self, attr_length))
        start = min(start, max_start)
        slider.set(start)
        setattr(self, attr_start, start)
        label_update()
        self._auto_update_preview()

    def _on_year_slider_changed(self, value):
        self._handle_slider_change('year_start', 'year_length', self.year_slider, self._update_year_label)

    def _on_month_slider_changed(self, value):
        self._handle_slider_change('month_start', 'month_length', self.month_slider, self._update_month_label)

    def _on_day_slider_changed(self, value):
        self._handle_slider_change('day_start', 'day_length', self.day_slider, self._update_day_label)

    def _on_month_textual_changed(self):
        if self.month_textual_var.get():
            folder = self.parent.full_folder_path
            if folder:
                count = count_full_months_in_folder(folder)
                if count > 0 and messagebox.askyesno("Normalize?", f"{count} file(s) have full month names. Normalize?"):
                    renamed = normalize_full_months_in_folder(folder)
                    messagebox.showinfo("Done", f"Renamed {renamed} file(s).")
                    self.parent.file_name = None
                    self.parent.full_file_path = None
                    self.destroy()
                    messagebox.showinfo("Reselect Sample File", "Please re-select sample file.")
                    return
            self.month_length = 3
        else:
            self.month_length = 2

        self._auto_update_preview()

    def _on_day_enable_toggled(self):
        self.day_enabled = self.day_enable_var.get()

        if self.day_enabled:
            # Re-grid the Day slider and preview label
            self.day_slider.grid(row=2, column=1, sticky="ew", padx=(5, 5))
            self.day_substring_label.grid(row=2, column=3, sticky="e")
        else:
            # Hide slider and preview, leave checkbox intact
            self.day_slider.grid_remove()
            self.day_substring_label.grid_remove()

        self._auto_update_preview()

    def _update_label(self, start_attr, length_attr, label_widget):
        if self.file_length == 0:
            label_widget.configure(text="[--]")
            return
        start = getattr(self, start_attr)
        end = start + getattr(self, length_attr)
        sub = self.sample_filename[start:end]
        label_widget.configure(text=f"[{sub}]")

    def _update_year_label(self):
        self._update_label('year_start', 'year_length', self.year_substring_label)

    def _update_month_label(self):
        self._update_label('month_start', 'month_length', self.month_substring_label)

    def _update_day_label(self):
        self._update_label('day_start', 'day_length', self.day_substring_label)

    def _update_all_substring_labels(self):
        self._update_year_label()
        self._update_month_label()
        self._update_day_label()

    def _auto_update_preview(self):
        if not self.parent.file_name:
            self.preview_var.set("")
            return

        prefix = self.prefix_var.get()
        y, yl = self.year_start, self.year_length
        m, ml = self.month_start, self.month_length
        d = self.day_start if self.day_enabled else None
        dl = self.day_length if self.day_enabled else None

        try:
            year, month, day = parse_filename_position_based(
                self.parent.file_name,
                year_start=y, year_length=yl,
                month_start=m, month_length=ml,
                day_start=d, day_length=dl,
                textual_month=self.month_textual_var.get()
            )
            new_base = build_new_filename(prefix, year, month, day)
            ext = os.path.splitext(self.parent.file_name)[1]
            self.preview_var.set(new_base + ext)
        except Exception:
            self.preview_var.set("")

    def _on_rename_all(self):
        if not self.parent.full_folder_path:
            messagebox.showerror("No Folder", "Please select a target folder.")
            return

        if not messagebox.askyesno("Confirm", "Rename all files?"):
            return

        args = {
            "year_start": self.year_start, "year_length": self.year_length,
            "month_start": self.month_start, "month_length": self.month_length
        }
        if self.day_enabled:
            args["day_start"] = self.day_start
            args["day_length"] = self.day_length

        try:
            result = rename_files_in_folder(
                folder_path=self.parent.full_folder_path,
                prefix=self.prefix_var.get(),
                position_args=args,
                textual_month=self.month_textual_var.get(),
                dry_run=False,
                expected_length = len(self.sample_filename)
            )

            # Format renamed files
            renamed_msg = "\n".join(f"{o} -> {n}" for o, n in result["renamed"])
            summary = (
                f"Total files scanned: {result['total']}\n"
                f"Successfully renamed: {result['successful']}\n"
                f"Skipped: {result['failed']}"
            )

            messagebox.showinfo("Rename Complete", summary)

            # Optional: show skipped files separately
            if result["skipped"]:
                skipped_list = "\n".join(result["skipped"])
                messagebox.showwarning("Skipped Files", f"Skipped due to parsing errors:\n{skipped_list}")

        except Exception as e:
            messagebox.showerror("Rename Error", str(e))
