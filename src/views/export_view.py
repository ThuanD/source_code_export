import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from pathlib import Path
from typing import Dict, Any, Callable, List
from datetime import datetime

from src.views.base_view import BaseView


class ExportView(BaseView):
    """View for configuring and running an export."""

    def __init__(self, *args, **kwargs):
        """Initialize the export view."""
        super().__init__(*args, **kwargs)

        # Input values
        self.input_folder_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.exclude_paths_var = tk.StringVar()
        self.exclude_extensions_var = tk.StringVar()
        self.output_format_var = tk.StringVar(value="txt")
        self.exclude_size_var = tk.StringVar(value="0")

        # Progress tracking
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="")

    def create_widgets(self) -> None:
        """Create the export view widgets with a robust button layout."""
        self.frame = self.create_themed_frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        content_container = self.create_themed_frame(self.frame)
        content_container.grid(row=0, column=0, sticky="nsew")
        content_container.grid_rowconfigure(0, weight=1)
        content_container.grid_columnconfigure(0, weight=1)

        colors = self.theme_manager.get_current_theme_colors()
        canvas = tk.Canvas(
            content_container, highlightthickness=0, background=colors["bg_primary"]
        )
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            content_container, orient="vertical", command=canvas.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = self.create_themed_frame(canvas)
        scrollable_frame.columnconfigure(0, weight=1)

        scrollable_frame.grid_rowconfigure(1, weight=1)

        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", update_scrollregion)

        def update_frame_width(event):
            canvas.itemconfig(frame_id, width=event.width)

        canvas.bind("<Configure>", update_frame_width)

        current_row = 0

        title_frame = self.create_themed_frame(scrollable_frame)
        title_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 16))
        current_row += 1
        title_label = self.create_title_label(
            title_frame, self._("export_configuration")
        )
        title_label.pack(side=tk.LEFT, pady=8)

        notebook = ttk.Notebook(scrollable_frame)
        notebook.grid(row=current_row, column=0, sticky="nsew")
        current_row += 1

        basic_tab = self.create_themed_frame(notebook)
        notebook.add(basic_tab, text=self._("basic_settings"))
        self._create_basic_settings_tab(basic_tab)

        advanced_tab = self.create_themed_frame(notebook)
        notebook.add(advanced_tab, text=self._("advanced_settings"))
        self._create_advanced_settings_tab(advanced_tab)

        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=current_row, column=0, sticky="ew", pady=10
        )
        current_row += 1

        progress_container = self.create_themed_frame(scrollable_frame)
        progress_container.grid(row=current_row, column=0, sticky="ew", padx=5)
        current_row += 1

        progress_label = self.create_themed_label(
            progress_container, self._("export_progress")
        )
        progress_label.pack(anchor="w")

        self.progress_section = {}
        self.progress_section["bar"] = ttk.Progressbar(
            progress_container,
            orient="horizontal",
            mode="determinate",
            variable=self.progress_var,
        )
        self.progress_section["bar"].pack(fill=tk.X, pady=(2, 0))

        self.progress_section["status"] = self.create_caption_label(
            progress_container, ""
        )
        self.progress_section["status"]["textvariable"] = self.status_var
        self.progress_section["status"].pack(anchor="w")

        bottom_bar = self.create_themed_frame(self.frame)
        bottom_bar.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        bottom_bar.grid_columnconfigure(1, weight=1)

        left_buttons_frame = self.create_themed_frame(bottom_bar)
        left_buttons_frame.grid(row=0, column=0, sticky="w")

        self.widgets["back_button"] = self.create_themed_button(
            left_buttons_frame, text=self._("back_to_list"), command=self._on_back
        )
        self.widgets["back_button"].pack(side=tk.LEFT, padx=(0, 5))

        self.widgets["delete_button"] = self.create_themed_button(
            left_buttons_frame,
            text=self._("delete_config"),
            command=self._on_delete_config,
            style="Danger.TButton",
        )
        self.widgets["delete_button"].pack(side=tk.LEFT)

        right_buttons_frame = self.create_themed_frame(bottom_bar)
        right_buttons_frame.grid(row=0, column=2, sticky="e")
        self.widgets["right_buttons_frame"] = right_buttons_frame

        self.widgets["run_button"] = self.create_themed_button(
            right_buttons_frame,
            text=self._("run_export"),
            command=self._on_run_export,
            style="Success.TButton",
        )
        self.widgets["run_button"].pack()

    def _create_basic_settings_tab(self, parent: tk.Widget) -> None:
        """Create the basic settings tab content to match the desired UI."""

        # --- Input Folder ---
        input_frame = self.create_themed_frame(parent)
        input_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

        input_label = self.create_themed_label(input_frame, self._("input_folder"))
        input_label.pack(anchor="w")

        input_entry_frame = self.create_themed_frame(input_frame)
        input_entry_frame.pack(fill=tk.X)

        self.widgets["input_entry"] = self.create_themed_entry(
            input_entry_frame, textvariable=self.input_folder_var
        )
        self.widgets["input_entry"].pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
        )
        self.widgets["input_entry"].bind("<FocusOut>", self._update_output_filename)

        self.widgets["browse_input_button"] = self.create_themed_button(
            input_entry_frame, text=self._("browse"), command=self._browse_input_folder
        )
        self.widgets["browse_input_button"].pack(side=tk.LEFT)

        # --- Output File ---
        output_frame = self.create_themed_frame(parent)
        output_frame.pack(fill=tk.X, padx=5, pady=5)

        output_label = self.create_themed_label(output_frame, self._("output_file"))
        output_label.pack(anchor="w")

        output_entry_frame = self.create_themed_frame(output_frame)
        output_entry_frame.pack(fill=tk.X)

        self.widgets["output_entry"] = self.create_themed_entry(
            output_entry_frame, textvariable=self.output_file_var
        )
        self.widgets["output_entry"].pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
        )

        self.widgets["browse_output_button"] = self.create_themed_button(
            output_entry_frame, text=self._("browse"), command=self._browse_output_file
        )
        self.widgets["browse_output_button"].pack(side=tk.LEFT)

        # --- Output Format ---
        format_frame = self.create_themed_frame(parent)
        format_frame.pack(fill=tk.X, padx=5, pady=(10, 0))

        format_label = self.create_themed_label(format_frame, self._("output_format"))
        format_label.pack(anchor="w")

        format_options_frame = self.create_themed_frame(format_frame)
        format_options_frame.pack(fill=tk.X)

        format_options = [
            ("text_format", "txt"),
            ("markdown_format", "md"),
            ("html_format", "html"),
            ("json_format", "json"),
        ]

        for text_key, value in format_options:
            rb = ttk.Radiobutton(
                format_options_frame,
                text=self._(text_key),
                variable=self.output_format_var,
                value=value,
                command=self._update_output_file_extension,
            )
            rb.pack(side=tk.LEFT, padx=(0, 15), pady=2)

        # --- Other Options (Checkboxes) ---
        options_frame = self.create_themed_frame(parent)
        options_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

    def _create_advanced_settings_tab(self, parent: tk.Widget) -> None:
        """Create the advanced settings tab content."""
        # Exclude paths
        exclude_paths_frame = self.create_themed_frame(parent)
        exclude_paths_frame.pack(fill=tk.X, pady=5)

        exclude_paths_label_frame = self.create_themed_frame(exclude_paths_frame)
        exclude_paths_label_frame.pack(fill=tk.X)

        exclude_paths_label = self.create_themed_label(
            exclude_paths_label_frame, self._("exclude_paths")
        )
        exclude_paths_label.pack(side=tk.LEFT, pady=(0, 5))

        help_button = self.create_themed_button(
            exclude_paths_label_frame,
            text="?",
            command=self._show_exclude_paths_help,
            width=2,
        )
        help_button.pack(side=tk.RIGHT)
        self._create_tooltip(exclude_paths_label, "exclude_paths_tooltip")
        self._create_tooltip(help_button, "help_tooltip")

        exclude_paths_entry_frame = self.create_themed_frame(exclude_paths_frame)
        exclude_paths_entry_frame.pack(fill=tk.X)

        exclude_paths_entry = self.create_themed_entry(
            exclude_paths_entry_frame, textvariable=self.exclude_paths_var
        )
        exclude_paths_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_exclude_button = self.create_themed_button(
            exclude_paths_entry_frame,
            text=self._("browse"),
            command=self._browse_exclude_paths,
            width=3,
        )
        browse_exclude_button.pack(side=tk.RIGHT)
        self._create_tooltip(exclude_paths_entry, "exclude_paths_entry_tooltip")
        self._create_tooltip(browse_exclude_button, "select_folder_tooltip")

        # Exclude extensions
        exclude_ext_frame = self.create_themed_frame(parent)
        exclude_ext_frame.pack(fill=tk.X, pady=5)

        exclude_ext_label_frame = self.create_themed_frame(exclude_ext_frame)
        exclude_ext_label_frame.pack(fill=tk.X)

        exclude_ext_label = self.create_themed_label(
            exclude_ext_label_frame, self._("exclude_extensions")
        )
        exclude_ext_label.pack(side=tk.LEFT, pady=(0, 5))

        ext_help_button = self.create_themed_button(
            exclude_ext_label_frame,
            text="?",
            command=self._show_exclude_extensions_help,
            width=2,
        )
        ext_help_button.pack(side=tk.RIGHT)
        self._create_tooltip(exclude_ext_label, "exclude_extensions_tooltip")
        self._create_tooltip(ext_help_button, "help_tooltip")

        exclude_ext_entry = self.create_themed_entry(
            exclude_ext_frame, textvariable=self.exclude_extensions_var
        )
        exclude_ext_entry.pack(fill=tk.X)
        self._create_tooltip(exclude_ext_entry, "exclude_extensions_entry_tooltip")

        # Exclude files larger than
        size_frame = self.create_themed_frame(parent)
        size_frame.pack(fill=tk.X, pady=5)

        size_label = self.create_themed_label(size_frame, self._("exclude_size_above"))
        size_label.pack(anchor=tk.W, pady=(0, 5))

        # Only allow numeric input
        vcmd = (parent.register(self._validate_numeric), "%P")
        size_entry = ttk.Entry(
            size_frame,
            textvariable=self.exclude_size_var,
            validate="key",
            validatecommand=vcmd,
            width=10,
        )
        size_entry.pack(anchor=tk.W)
        self._create_tooltip(size_label, "exclude_size_tooltip")
        self._create_tooltip(size_entry, "exclude_size_entry_tooltip")

        # Example settings
        examples_frame = self.create_themed_frame(parent)
        examples_frame.pack(fill=tk.X, pady=5)

        examples_label = self.create_themed_label(
            examples_frame,
            self._("common_exclude_patterns", "Common Exclude Patterns:"),
            style="Header.TLabel",
        )
        examples_label.pack(anchor=tk.W, pady=(10, 5))

        examples = [
            self._("exclude_node_modules", "• node_modules: JavaScript dependencies"),
            self._("exclude_venv", "• venv, .venv: Python virtual environments"),
            self._("exclude_build", "• build, dist: Build artifacts"),
            self._("exclude_ide", "• .idea, .vscode: IDE settings"),
            self._("exclude_git", "• .git: Git repository"),
        ]

        for example in examples:
            example_label = self.create_themed_label(examples_frame, example)
            example_label.pack(anchor=tk.W, padx=10)
        self._create_tooltip(examples_label, "examples_tooltip")

    def set_callbacks(
        self,
        on_back: Callable = None,
        on_delete_config: Callable = None,
        on_run_export: Callable = None,
    ) -> None:
        """Set callbacks for user actions."""
        self._on_back_callback = on_back
        self._on_delete_config_callback = on_delete_config
        self._on_run_export_callback = on_run_export

    def set_values(self, config: Dict[str, Any]) -> None:
        """Set form values from a configuration dictionary."""
        self.input_folder_var.set(config.get("input_folder", ""))
        self.output_file_var.set(config.get("output_file", ""))
        self.exclude_paths_var.set(" ".join(config.get("exclude_paths", [])))
        self.exclude_extensions_var.set(" ".join(config.get("exclude_extensions", [])))
        self.output_format_var.set(config.get("output_format", "txt"))
        self.exclude_size_var.set(str(config.get("exclude_size_above", 0)))

    def get_values(self) -> Dict[str, Any]:
        """Get form values as a configuration dictionary."""
        # Parse exclude paths
        exclude_paths = []
        if self.exclude_paths_var.get().strip():
            exclude_paths = self.exclude_paths_var.get().strip().split()

        # Parse exclude extensions
        exclude_extensions = []
        if self.exclude_extensions_var.get().strip():
            exclude_extensions = self.exclude_extensions_var.get().strip().split()

        # Convert exclude size to int
        try:
            exclude_size = int(self.exclude_size_var.get().strip() or "0")
        except ValueError:
            exclude_size = 0

        return {
            "input_folder": self.input_folder_var.get().strip(),
            "output_file": self.output_file_var.get().strip(),
            "exclude_paths": exclude_paths,
            "exclude_extensions": exclude_extensions,
            "output_format": self.output_format_var.get(),
            "exclude_size_above": exclude_size,
        }

    def validate(self) -> bool:
        """Validate form values."""
        # Check input folder
        input_folder = self.input_folder_var.get().strip()
        if not input_folder:
            messagebox.showerror(
                self._("error"),
                self._("input_folder_required", "Input folder is required."),
                parent=self.parent,
            )
            return False

        if not Path(input_folder).exists():
            messagebox.showerror(
                self._("error"),
                self._("input_folder_not_exists", "Input folder does not exist."),
                parent=self.parent,
            )
            return False

        # Check output file
        output_file = self.output_file_var.get().strip()
        if not output_file:
            messagebox.showerror(
                self._("error"),
                self._("output_file_required", "Output file is required."),
                parent=self.parent,
            )
            return False

        # Ensure output file directory exists
        output_path = Path(output_file)
        if not output_path.parent.exists():
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror(
                    self._("error"),
                    self._(
                        "cannot_create_output_dir",
                        "Cannot create output directory: {0}",
                        str(e),
                    ),
                    parent=self.parent,
                )
                return False

        # Validate exclude size is an integer
        try:
            exclude_size = int(self.exclude_size_var.get().strip() or "0")
            if exclude_size < 0:
                messagebox.showerror(
                    self._("error"),
                    self._("size_must_be_positive", "Size must be a positive number."),
                    parent=self.parent,
                )
                return False
        except ValueError:
            messagebox.showerror(
                self._("error"),
                self._("size_must_be_integer", "Size must be a valid integer."),
                parent=self.parent,
            )
            return False

        return True

    def update_progress(self, progress: float, status: str) -> None:
        """Update progress bar and status."""
        self.progress_var.set(progress * 100)
        self.status_var.set(status)

        # Ensure UI updates
        self.frame.update_idletasks()

        # Show the open file button if the export is complete
        if progress >= 1.0:
            self._show_open_file_button()
        else:
            self._hide_open_file_button()

    def set_running_state(self, is_running: bool) -> None:
        """Enable/disable run button and set running state."""
        if is_running:
            self.widgets["run_button"].configure(
                text=self._("running", "Running..."), state=tk.DISABLED
            )
        else:
            self.widgets["run_button"].configure(
                text=self._("run_export"), state=tk.NORMAL
            )

    def on_theme_change(self) -> None:
        """Handle theme changes."""
        super().on_theme_change()

    def refresh_translations(self) -> None:
        """Refresh all translations in the view."""
        # Store current values
        current_values = self.get_values()

        # Destroy and recreate widgets
        self.destroy()
        self.create_widgets()

        # Restore values
        self.set_values(current_values)

        # Re-register callbacks
        if hasattr(self, "_on_back_callback"):
            # Find back button in button group
            button_frame = self.frame.winfo_children()[-1]  # Last child is button frame
            back_button = button_frame.winfo_children()[
                0
            ]  # First button is back button
            back_button.configure(command=self._on_back)
        if hasattr(self, "_on_delete_config_callback"):
            # Find delete button in button group
            button_frame = self.frame.winfo_children()[-1]  # Last child is button frame
            delete_button = button_frame.winfo_children()[
                1
            ]  # Second button is delete button
            delete_button.configure(command=self._on_delete_config)
        if hasattr(self, "_on_run_export_callback"):
            # Find run button in button group
            button_frame = self.frame.winfo_children()[-1]  # Last child is button frame
            run_button = button_frame.winfo_children()[-1]  # Last button is run button
            run_button.configure(command=self._on_run_export)

    def _show_open_file_button(self) -> None:
        """Show open file button."""
        if "open_file_button" not in self.widgets:
            output_file = self.output_file_var.get().strip()
            if output_file:
                open_button = self.create_themed_button(
                    self.widgets["right_buttons_frame"],
                    text=self._("open_output_file", "Open Output"),
                    command=lambda: self._open_output_file(output_file),
                    style="TButton",
                )
                open_button.pack(pady=(4, 0))
                self.widgets["open_file_button"] = open_button

    def _hide_open_file_button(self) -> None:
        """Hide and cancel open file button."""
        if "open_file_button" in self.widgets:
            self.widgets["open_file_button"].destroy()
            del self.widgets["open_file_button"]

    def _open_output_file(self, file_path: str) -> None:
        """Open ouput file using default app."""
        try:
            import webbrowser

            output_path = Path(file_path)
            if output_path.exists():
                webbrowser.open(file_path)
            else:
                messagebox.showwarning(
                    self._("warning"),
                    self._("file_not_found", "File not found."),
                    parent=self.parent,
                )
        except Exception as e:
            logging.error(f"Error opening output file: {e}")
            messagebox.showerror(self._("error"), str(e), parent=self.parent)

    def _browse_input_folder(self) -> None:
        """Browse for input folder."""
        folder = filedialog.askdirectory(
            title=self._("select_input_folder", "Select Input Folder"),
            initialdir=self.input_folder_var.get() or Path.home(),
        )

        if folder:
            self.input_folder_var.set(folder)

            # Set a default output file name based on folder name
            if not self.output_file_var.get():
                folder_path = Path(folder)
                output_file = (
                    folder_path.parent
                    / f"{folder_path.name}_export.{self.output_format_var.get()}"
                )
                self.output_file_var.set(str(output_file))

    def _browse_output_file(self) -> None:
        """Browse for output file."""
        # Create a dictionary of file types for different formats
        filetypes = {
            "txt": [("Text Files", "*.txt"), ("All Files", "*.*")],
            "md": [("Markdown Files", "*.md"), ("All Files", "*.*")],
            "html": [("HTML Files", "*.html"), ("All Files", "*.*")],
            "json": [("JSON Files", "*.json"), ("All Files", "*.*")],
        }

        current_format = self.output_format_var.get()

        file = filedialog.asksaveasfilename(
            title=self._("select_output_file", "Select Output File"),
            initialdir=Path(self.output_file_var.get()).parent
            if self.output_file_var.get()
            else Path.home(),
            initialfile=Path(self.output_file_var.get()).name
            if self.output_file_var.get()
            else f"export.{current_format}",
            defaultextension=f".{current_format}",
            filetypes=filetypes.get(current_format, [("All Files", "*.*")]),
        )

        if file:
            self.output_file_var.set(file)

    def _show_exclude_paths_help(self) -> None:
        """Show help for exclude paths."""
        MessageDialog(
            self.parent,
            self._("exclude_paths_help_title"),
            [
                self._("exclude_paths_help"),
                "",
                self._("exclude_paths_example1"),
                self._("exclude_paths_example2"),
                self._("exclude_paths_example3"),
            ],
            self.theme_manager,
        )

    def _show_exclude_extensions_help(self) -> None:
        """Show help for exclude extensions."""
        MessageDialog(
            self.parent,
            self._("exclude_extensions_help_title"),
            [
                self._("exclude_extensions_help"),
                "",
                self._("exclude_extensions_example"),
            ],
            self.theme_manager,
        )

    def _validate_numeric(self, value: str) -> bool:
        """Validate that entry contains only digits."""
        if value == "":
            return True
        return value.isdigit()

    def _on_back(self) -> None:
        """Handle back button click."""
        if hasattr(self, "_on_back_callback") and self._on_back_callback:
            self._on_back_callback()

    def _on_delete_config(self) -> None:
        """Handle delete config button click."""
        if (
            not hasattr(self, "_on_delete_config_callback")
            or not self._on_delete_config_callback
        ):
            return

        # Confirm deletion
        if messagebox.askyesno(
            self._("warning"), self._("confirm_delete_config"), parent=self.parent
        ):
            self._on_delete_config_callback()

    def _on_run_export(self) -> None:
        """Handle run export button click."""
        if (
            not hasattr(self, "_on_run_export_callback")
            or not self._on_run_export_callback
        ):
            return

        if self.validate():
            config = self.get_values()
            self._on_run_export_callback(config)

    def _browse_exclude_paths(self):
        """Browse to select files and folders to exclude."""
        dialog_title = self._("select_exclude_folder")
        dialog_message = self._("select_multiple_files_folders")

        dialog = tk.Toplevel(self.parent)
        dialog.title(dialog_title)
        dialog.transient(self.parent)
        dialog.grab_set()

        # Center the dialog on the parent window
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (300 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (150 // 2)
        dialog.geometry(f"300x120+{x}+{y}")
        dialog.resizable(False, False)

        # Message
        message_label = ttk.Label(dialog, text=dialog_message, wraplength=280)
        message_label.pack(pady=10)

        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        # Button for selecting files
        files_button = ttk.Button(
            button_frame,
            text=self._("select_files_button"),
            command=lambda: [dialog.destroy(), self._select_files_to_exclude()],
        )
        files_button.grid(row=0, column=0, padx=5, pady=5)

        # Button for selecting folders
        folders_button = ttk.Button(
            button_frame,
            text=self._("select_folders_button"),
            command=lambda: [dialog.destroy(), self._select_folders_to_exclude()],
        )
        folders_button.grid(row=0, column=1, padx=5, pady=5)

        dialog.wait_window()

    def _select_files_to_exclude(self):
        """Select files to exclude."""
        input_path = self.input_folder_var.get().strip()
        if not input_path:
            messagebox.showwarning(
                self._("warning_title", "Warning"),
                self._("no_input_path", "Please select an input folder first"),
            )
            return

        try:
            # Chuyển đổi input_path thành đường dẫn tuyệt đối
            input_path_abs = Path(input_path).resolve()

            # Mở dialog trong thư mục input để dễ chọn đường dẫn tương đối
            files = filedialog.askopenfilenames(
                title=self._("select_exclude_folder"),
                initialdir=input_path_abs,
                parent=self.parent,
            )

            if files:
                self._add_exclude_paths(files)
        except Exception as e:
            logging.error(f"Error selecting files: {e}")
            messagebox.showerror(self._("error", "Error"), str(e))

    def _select_folders_to_exclude(self):
        """Select folders to exclude."""
        input_path = self.input_folder_var.get().strip()
        if not input_path:
            messagebox.showwarning(
                self._("warning_title", "Warning"),
                self._("no_input_path", "Please select an input folder first"),
            )
            return

        try:
            # Chuyển đổi input_path thành đường dẫn tuyệt đối
            input_path_abs = Path(input_path).resolve()

            # Mở dialog trong thư mục input để dễ chọn đường dẫn tương đối
            folder = filedialog.askdirectory(
                title=self._("select_exclude_folder"),
                initialdir=input_path_abs,
                parent=self.parent,
            )

            if folder:
                self._add_exclude_paths([folder])
        except Exception as e:
            logging.error(f"Error selecting folder: {e}")
            messagebox.showerror(self._("error", "Error"), str(e))

    def _add_exclude_paths(self, paths):
        """Add the selected paths to the exclude paths list."""
        if not paths:
            return

        input_path = self.input_folder_var.get().strip()
        if not input_path:
            messagebox.showwarning(
                self._("warning_title", "Warning"),
                self._("no_input_path", "Please select an input folder first"),
            )
            return

        # Đảm bảo input_path là đường dẫn tuyệt đối
        input_path_abs = Path(input_path).resolve()

        # Chuyển đổi tất cả các đường dẫn thành đường dẫn tương đối
        relative_paths = []
        for path in paths:
            try:
                # Chuyển đổi path thành đường dẫn tuyệt đối
                path_abs = Path(path).resolve()

                # Tạo đường dẫn tương đối
                try:
                    rel_path = path_abs.relative_to(input_path_abs)
                    path_str = str(rel_path).replace("\\", "/")
                    relative_paths.append(path_str)
                except ValueError:
                    # Nếu đường dẫn không nằm trong thư mục input, hiển thị cảnh báo
                    messagebox.showwarning(
                        self._("warning_title", "Warning"),
                        self._(
                            "path_outside_input", "Path is outside input folder: {0}"
                        ).format(path),
                    )
            except Exception as e:
                logging.error(f"Error creating relative path for {path}: {e}")
                messagebox.showwarning(
                    self._("warning_title", "Warning"),
                    self._(
                        "error_relative_path", "Error creating relative path: {0}"
                    ).format(str(e)),
                )

        if not relative_paths:
            return

        # Thêm vào danh sách đường dẫn loại trừ
        current_paths = self.exclude_paths_var.get().strip()
        path_list = (
            [p for p in current_paths.split(" ") if p.strip()] if current_paths else []
        )

        # Thêm các đường dẫn mới nếu chưa có trong danh sách
        added = 0
        for path in relative_paths:
            if path not in path_list:
                path_list.append(path)
                added += 1

        # Cập nhật biến exclude_paths
        self.exclude_paths_var.set(" ".join(path_list))

        # Hiển thị thông báo phản hồi
        if added > 0:
            self.status_var.set(
                self._("paths_excluded", "{0} paths excluded").format(added)
            )

    def _update_output_filename(self, event=None) -> None:
        """Update output filename automatically based on input folder and format."""
        input_folder = self.input_folder_var.get().strip()
        current_output = self.output_file_var.get().strip()

        # Only update if output is empty or user hasn't manually changed it
        if not input_folder or (
            current_output and not hasattr(self, "_auto_generated_output")
        ):
            return

        try:
            # Get folder name from path
            folder_path = Path(input_folder)
            folder_name = folder_path.name

            # Create output filename
            output_format = self.output_format_var.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{folder_name}_export_{timestamp}.{output_format}"

            # Set default location next to the input folder
            output_path = folder_path.parent / output_filename

            # Update output file
            self.output_file_var.set(str(output_path))
            self._auto_generated_output = True
        except Exception as e:
            logging.warning(f"Error generating output filename: {e}")

    def _update_output_file_extension(self, event=None) -> None:
        """Update output file extension when format changes."""
        output_file = self.output_file_var.get().strip()
        if not output_file:
            return

        try:
            output_path = Path(output_file)
            new_format = self.output_format_var.get()

            # Change extension
            new_output = output_path.with_suffix(f".{new_format}")
            self.output_file_var.set(str(new_output))
        except Exception as e:
            logging.warning(f"Error updating output file extension: {e}")

    def _create_tooltip(self, widget, text_key):
        """Create a tooltip for a widget.

        Args:
            widget: The widget to create a tooltip for
            text_key: The translation key for the tooltip text
        """
        text = self._(text_key) if isinstance(text_key, str) else text_key
        ToolTip(widget, text)


class MessageDialog:
    """Simple dialog for displaying messages."""

    def __init__(
        self, parent: tk.Widget, title: str, messages: List[str], theme_manager=None
    ):
        """Initialize and show dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.resizable(False, False)

        # Center on parent
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (300 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (200 // 2)
        self.dialog.geometry(f"350x200+{x}+{y}")

        # Set theme
        if theme_manager:
            colors = theme_manager.get_current_theme_colors()
            self.dialog.configure(bg=colors["bg_primary"])

        # Message frame
        message_frame = tk.Frame(
            self.dialog, bg=colors["bg_primary"] if theme_manager else None
        )
        message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add message labels
        for message in messages:
            if message:
                label = tk.Label(
                    message_frame,
                    text=message,
                    anchor="w",
                    justify="left",
                    bg=colors["bg_primary"] if theme_manager else None,
                    fg=colors["fg_primary"] if theme_manager else None,
                )
                label.pack(fill=tk.X, pady=2)
            else:
                # Empty string adds a spacer
                tk.Frame(
                    message_frame,
                    height=10,
                    bg=colors["bg_primary"] if theme_manager else None,
                ).pack(fill=tk.X)

        # OK button
        button_frame = tk.Frame(
            self.dialog, bg=colors["bg_primary"] if theme_manager else None
        )
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        ok_button = tk.Button(
            button_frame,
            text="OK",
            width=10,
            command=self.dialog.destroy,
            bg=colors["accent"] if theme_manager else None,
            fg="white" if theme_manager else None,
            relief=tk.FLAT,
        )
        ok_button.pack(pady=5)

        # Make dialog modal
        self.dialog.grab_set()
        parent.wait_window(self.dialog)


class ToolTip:
    """Tooltip class for creating tooltips for widgets."""

    def __init__(self, widget, text):
        """Initialize the tooltip.

        Args:
            widget: The widget to attach the tooltip to
            text: The text to display in the tooltip
        """
        self.widget = widget
        self.text = text
        self.tooltip = None

        # Bind events
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        """Show the tooltip when mouse enters the widget."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Create a toplevel window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        # Get colors from theme manager if available
        bg_color = "#f5f5f5"  # Default light background
        fg_color = "#333333"  # Default dark text

        if hasattr(self.widget, "master") and hasattr(
            self.widget.master, "theme_manager"
        ):
            try:
                colors = self.widget.master.theme_manager.get_current_theme_colors()
                bg_color = colors.get("bg_tertiary", bg_color)
                fg_color = colors.get("fg_primary", fg_color)
            except (AttributeError, KeyError):
                pass

        # Create frame and label
        frame = tk.Frame(
            self.tooltip, background=bg_color, borderwidth=1, relief="solid"
        )
        frame.pack(ipadx=5, ipady=5)

        label = tk.Label(
            frame,
            text=self.text,
            background=bg_color,
            foreground=fg_color,
            justify="left",
            wraplength=250,
        )
        label.pack()

    def leave(self, event=None):
        """Hide the tooltip when mouse leaves the widget."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
