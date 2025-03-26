import logging
import json
import os
import sys
import webbrowser
import threading
import queue
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from dialog import ExcludePathHelpDialog, ExcludeExtensionHelpDialog
from source_code_export import SourceCodeExporter

# --- Constants ---
APP_NAME = "Source Code Exporter"
HISTORY_FILENAME = "export_history.json"
LOG_FILENAME = "app.log"
DEFAULT_OUTPUT_FILENAME = "source_code_export.txt"


# --- Helper Function for PyInstaller ---
def get_app_dir() -> Path:
    """Gets the directory where the application executable or script is located."""
    if getattr(sys, "frozen", False):
        # Running as a bundled executable (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Running as a normal Python script
        return Path(__file__).parent


# --- Logging Configuration ---
APP_DIR = get_app_dir()
LOG_FILE_PATH = APP_DIR / LOG_FILENAME

# Configure root logger
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Console Handler (for running as script)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setFormatter(log_formatter)
# logger.addHandler(stream_handler)

# File Handler (always useful, especially for bundled app)
try:
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    print(f"Error setting up file logging: {e}")  # Print error if logging fails

logger.info("Application started.")
logger.info(f"Application directory: {APP_DIR}")
logger.info(f"Log file: {LOG_FILE_PATH}")


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.app_dir = APP_DIR
        self.history_file = self.app_dir / HISTORY_FILENAME
        logger.info(f"History file location: {self.history_file}")

        self.history = self.load_history()
        self.export_queue = queue.Queue()  # Queue for thread communication
        self.run_button = None  # To disable/enable Run button

        self.root.title(APP_NAME)
        self.root.geometry("700x500")  # Increased size slightly

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle closing

        self.create_main_list_view()

    def on_closing(self):
        """Handle application closing."""
        logger.info("Application closing.")
        self.save_history()  # Ensure history is saved on exit
        self.root.destroy()

    def create_main_list_view(self):
        """Creates the main view showing the export history."""
        logger.debug("Creating main list view.")
        self._clear_widgets()

        ttk.Label(
            self.root, text="Source Code Export History", font=("Arial", 16)
        ).pack(pady=10)

        list_frame = ttk.Frame(self.root)
        list_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.tree = ttk.Treeview(
            list_frame, columns=("Path", "Last Run"), show="headings"
        )
        self.tree.heading("Path", text="Project Path")
        self.tree.heading("Last Run", text="Last Run")
        self.tree.column("Path", width=450, anchor="w")  # Left Alignment
        self.tree.column("Last Run", width=150, anchor="center")  # Center

        self._populate_treeview()

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.bind("<Double-1>", self.open_details)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="New Export", command=self.create_new_export).pack(
            side="left", padx=5
        )
        ttk.Button(
            btn_frame, text="Delete Selected", command=self.delete_selected
        ).pack(side="left", padx=5)

    def _populate_treeview(self):
        """Clears and repopulates the history Treeview."""
        # Clear existing items first
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Populate
        # Sort history items by path for consistent display
        sorted_history = sorted(self.history.items())
        for path, details in sorted_history:
            last_run_ts = details.get("last_run")
            last_run_str = "N/A"
            if last_run_ts:
                try:
                    last_run_str = datetime.fromtimestamp(last_run_ts).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                except Exception:
                    logger.warning(f"Invalid timestamp for {path}: {last_run_ts}")
                    last_run_str = "Invalid Date"  # Or keep N/A
            self.tree.insert("", "end", values=(path, last_run_str), tags=(path,))

    def _clear_widgets(self):
        """Removes all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_new_export(self):
        """Opens the details view for a new export configuration."""
        logger.debug("Creating new export view.")
        self.open_details()  # Pass no event, no selection

    def delete_selected(self):
        """Deletes selected items from the history."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No items selected.", parent=self.root)
            return

        if messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_items)} selected history item(s)?",
            parent=self.root,
        ):
            deleted_count = 0
            for item in selected_items:
                try:
                    path = self.tree.item(item, "values")[0]
                    if path in self.history:
                        del self.history[path]
                        logger.info(f"Deleted history item: {path}")
                        deleted_count += 1
                except IndexError:
                    logger.warning(f"Could not get path for selected tree item: {item}")
                except Exception as e:
                    logger.error(f"Error deleting item {item}: {e}")

            if deleted_count > 0:
                self.save_history()
                # Refresh the view efficiently
                self._populate_treeview()  # Just repopulate instead of full recreate
            else:
                messagebox.showwarning(
                    "Warning", "Could not delete selected items.", parent=self.root
                )

    def open_details(self, event=None):
        """Opens the details view for editing or creating an export config."""
        selected = self.tree.selection()
        path_key = None
        current_params = {}

        if event and selected:  # Check event to ensure it's from double-click
            try:
                path_key = self.tree.item(selected[0], "values")[0]
                if path_key in self.history:
                    current_params = self.history[path_key]
                    logger.debug(f"Opening details for existing entry: {path_key}")
                else:
                    logger.warning(
                        f"Path '{path_key}' selected but not found in history. Treating as new."
                    )
                    path_key = None  # Treat as new if data mismatch
            except IndexError:
                logger.warning(
                    "Could not get path from selected tree item on double-click."
                )

        # Provide sensible defaults if creating new or data is missing/invalid
        default_output_path = Path.home() / DEFAULT_OUTPUT_FILENAME
        final_params = {
            "path": current_params.get("path", ""),
            "output": current_params.get("output", str(default_output_path)),
            "exclude": current_params.get("exclude", []),
            "exclude_ext": current_params.get("exclude_ext", []),
        }

        # Store the original path key (if editing) to handle potential path changes
        self.original_path_key = path_key
        self.create_details_view(final_params)

    def create_details_view(self, params: dict):
        """Creates the view for editing export details."""
        logger.debug(f"Creating details view with params: {params}")
        self._clear_widgets()

        ttk.Label(self.root, text="Export Details", font=("Arial", 16)).pack(pady=10)

        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=5, fill="x")

        # --- Variables ---
        self.path_var = tk.StringVar(value=params.get("path", ""))
        self.output_var = tk.StringVar(value=params.get("output", ""))
        # Ensure exclude lists are strings for join
        exclude_list = params.get("exclude", [])
        exclude_ext_list = params.get("exclude_ext", [])
        self.exclude_var = tk.StringVar(value=" ".join(map(str, exclude_list)))
        self.exclude_ext_var = tk.StringVar(value=" ".join(map(str, exclude_ext_list)))

        # --- Input Fields ---
        fields = [
            ("Project Path", self.path_var, self.browse_input_folder, "Browse"),
            (
                "Output File",
                self.output_var,
                self.browse_output_file,
                "Browse",
            ),  # Changed command
            ("Exclude Paths", self.exclude_var, self.show_exclude_path_help, "Help"),
            (
                "Exclude Exts",
                self.exclude_ext_var,
                self.show_exclude_extension_help,
                "Help",
            ),
        ]

        for i, (label, var, command, btn_text) in enumerate(fields):
            ttk.Label(input_frame, text=label + ":").grid(
                row=i, column=0, padx=5, pady=5, sticky="w"
            )
            entry = ttk.Entry(
                input_frame, textvariable=var, width=60
            )  # Increased width
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            if command:
                ttk.Button(input_frame, text=btn_text, command=command).grid(
                    row=i, column=2, padx=5, pady=5
                )

        input_frame.columnconfigure(1, weight=1)  # Make entry field expand

        # --- Buttons Frame ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Back", command=self.create_main_list_view).pack(
            side="left", padx=5
        )
        # Assign Run button to instance variable
        self.run_button = ttk.Button(
            btn_frame, text="Run Export", command=self.run_export
        )
        self.run_button.pack(side="left", padx=5)
        # Only show Delete if editing an existing entry
        if self.original_path_key:
            ttk.Button(
                btn_frame, text="Delete This Entry", command=self.delete_current_export
            ).pack(side="left", padx=5)

    def browse_input_folder(self):
        """Opens a dialog to select the input project folder."""
        folder = filedialog.askdirectory(
            title="Select Project Folder", parent=self.root
        )
        if folder:
            folder_path = Path(folder)
            self.path_var.set(str(folder_path))
            # Suggest output file in the *parent* of the project folder or Home if root
            suggested_output_dir = (
                folder_path.parent if folder_path.parent != folder_path else Path.home()
            )
            output_file = (
                suggested_output_dir / f"{folder_path.name}_{DEFAULT_OUTPUT_FILENAME}"
            )
            self.output_var.set(str(output_file))
            logger.debug(
                f"Input folder selected: {folder}, suggested output: {output_file}"
            )

    def browse_output_file(self):
        """Opens a dialog to select the output file."""
        # Suggest a filename based on input path if possible
        initial_dir = Path.home()
        initial_file = DEFAULT_OUTPUT_FILENAME
        current_output = self.output_var.get()
        if current_output:
            try:
                current_path = Path(current_output)
                initial_dir = (
                    current_path.parent if current_path.parent.exists() else initial_dir
                )
                initial_file = current_path.name
            except Exception:
                logger.warning(
                    f"Could not parse current output path '{current_output}' for browser dialog."
                )

        filepath = filedialog.asksaveasfilename(
            title="Select Output File",
            initialdir=str(initial_dir),
            initialfile=initial_file,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            parent=self.root,
        )
        if filepath:
            self.output_var.set(filepath)
            logger.debug(f"Output file selected: {filepath}")

    def show_exclude_path_help(self):
        """Shows the help dialog for excluding paths."""
        ExcludePathHelpDialog(self.root, title="Exclude Paths Help")

    def show_exclude_extension_help(self):
        """Shows the help dialog for excluding extensions."""
        ExcludeExtensionHelpDialog(self.root, title="Exclude Extensions Help")

    def delete_current_export(self):
        """Deletes the currently viewed/edited history entry."""
        if not self.original_path_key:
            messagebox.showwarning(
                "Warning",
                "This is a new entry and cannot be deleted yet.",
                parent=self.root,
            )
            return

        if messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the history entry for:\n{self.original_path_key}?",
            parent=self.root,
        ):
            if self.original_path_key in self.history:
                del self.history[self.original_path_key]
                self.save_history()
                logger.info(
                    f"Deleted history entry via details view: {self.original_path_key}"
                )
                messagebox.showinfo(
                    "Deleted", "History entry deleted.", parent=self.root
                )
                self.create_main_list_view()  # Go back to main view
            else:
                messagebox.showerror(
                    "Error",
                    "Could not find the entry to delete. It might have been removed already.",
                    parent=self.root,
                )
                logger.warning(
                    f"Attempted to delete non-existent key from details view: {self.original_path_key}"
                )
                self.create_main_list_view()  # Go back anyway

    def _validate_path(self, path_str: str, check_exists: bool = True) -> Path | None:
        """Validates a path string, optionally checks existence, returns Path or None."""
        if not path_str:
            return None
        try:
            path = Path(path_str).resolve()
            if check_exists and not path.exists():
                return None
            return path
        except Exception as e:
            logger.error(f"Path validation error for '{path_str}': {e}")
            return None

    def run_export(self):
        """Initiates the export process in a separate thread."""
        input_path_str = self.path_var.get().strip()
        output_path_str = self.output_var.get().strip()
        exclude_str = self.exclude_var.get()
        exclude_ext_str = self.exclude_ext_var.get()

        # --- Basic Validation (in main thread) ---
        if not input_path_str:
            messagebox.showerror(
                "Error", "Project Path cannot be empty.", parent=self.root
            )
            return
        if not output_path_str:
            messagebox.showerror(
                "Error", "Output File cannot be empty.", parent=self.root
            )
            return

        input_path = self._validate_path(input_path_str, check_exists=True)
        if not input_path:
            messagebox.showerror(
                "Error",
                f"Input path does not exist or is invalid:\n{input_path_str}",
                parent=self.root,
            )
            return

        # Validate output path format (don't check existence yet, exporter handles dir creation)
        output_path = self._validate_path(output_path_str, check_exists=False)
        if not output_path:
            messagebox.showerror(
                "Error",
                f"Output file path is invalid:\n{output_path_str}",
                parent=self.root,
            )
            return

        # Parse excludes
        exclude_list = [p.strip() for p in exclude_str.split() if p.strip()]
        exclude_ext_list = [e.strip() for e in exclude_ext_str.split() if e.strip()]

        # --- Prepare for Thread ---
        if self.run_button:
            self.run_button.config(state=tk.DISABLED, text="Running...")

        export_params = {
            "input_path": str(input_path),  # Pass strings to thread
            "output_path": str(output_path),
            "exclude_paths": exclude_list,
            "exclude_extensions": exclude_ext_list,
        }

        logger.info(f"Starting export thread with params: {export_params}")

        # Start the export thread
        self.export_thread = threading.Thread(
            target=self._perform_export_thread,
            args=(export_params, self.export_queue),
            daemon=True,  # Allows app to exit even if thread is running (though queue check should handle it)
        )
        self.export_thread.start()

        # Start checking the queue for results
        self.root.after(100, self._check_export_status)

    def _perform_export_thread(self, params: dict, q: queue.Queue):
        """The actual export logic running in a separate thread."""
        try:
            input_path = Path(params["input_path"])
            output_path = Path(params["output_path"])

            # Create parent directory if it doesn't exist (important!)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            exporter = SourceCodeExporter(
                input_path,
                exclude_paths=params["exclude_paths"],
                exclude_extensions=params["exclude_extensions"],
            )
            exporter.export_structure(output_path)  # The potentially long operation

            # Success: Put result and config data into the queue
            result_data = {
                "success": True,
                "output_path": str(output_path),
                "config": {  # Data needed to update history
                    "path": str(input_path),
                    "output": str(output_path),
                    "exclude": params["exclude_paths"],
                    "exclude_ext": params["exclude_extensions"],
                    "last_run": output_path.stat().st_mtime,
                },
            }
            q.put(result_data)
            logger.info(f"Export thread finished successfully for {input_path}")

        except Exception as e:
            # Failure: Put error message into the queue
            error_message = f"Export failed: {str(e)}"
            logger.exception(
                f"Export thread failed for {params['input_path']}"
            )  # Log full traceback
            q.put({"success": False, "error": error_message})

    def _check_export_status(self):
        """Checks the queue for results from the export thread."""
        try:
            result = self.export_queue.get_nowait()

            # Re-enable button regardless of success/failure
            if self.run_button:
                self.run_button.config(state=tk.NORMAL, text="Run Export")

            if result["success"]:
                output_path = result["output_path"]
                config_data = result["config"]
                input_path_key = config_data["path"]

                # --- Update History ---
                # If the input path was changed, remove the old entry
                if self.original_path_key and self.original_path_key != input_path_key:
                    if self.original_path_key in self.history:
                        logger.info(
                            f"Input path changed. Removing old history key: {self.original_path_key}"
                        )
                        del self.history[self.original_path_key]

                # Add/Update the new entry
                self.history[input_path_key] = config_data
                self.save_history()
                logger.info(f"History updated/added for key: {input_path_key}")
                # Update the original key for the current view if it was just created
                self.original_path_key = input_path_key

                # --- Show Success Message & Offer to Open ---
                logger.info(f"Export completed: Output written to: {output_path}")
                if messagebox.askyesno(
                    "Export Success",
                    f"Export completed successfully!\nOutput written to: {output_path}\n\nDo you want to open the file?",
                    parent=self.root,
                ):
                    self.open_output_file(output_path)
            else:
                # --- Show Error Message ---
                messagebox.showerror("Error", result["error"], parent=self.root)

        except queue.Empty:
            # If queue is empty, check again later
            self.root.after(100, self._check_export_status)
        except Exception as e:
            # Handle unexpected errors during queue processing
            logger.exception("Error processing export queue result")
            messagebox.showerror(
                "Internal Error",
                f"An error occurred while processing the export result: {e}",
                parent=self.root,
            )
            if self.run_button:
                self.run_button.config(state=tk.NORMAL, text="Run Export")

    def open_output_file(self, file_path_str: str):
        """Opens the specified file using the default system handler."""
        logger.info(f"Attempting to open file: {file_path_str}")
        try:
            file_path = Path(file_path_str).resolve()  # Ensure absolute path
            if not file_path.exists():
                logger.error(f"Cannot open file - does not exist: {file_path}")
                messagebox.showerror(
                    "Error",
                    f"Cannot open file. File not found:\n{file_path}",
                    parent=self.root,
                )
                return

            # Use os.startfile on Windows, 'open' on macOS, xdg-open on Linux
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux and other POSIX
                os.system(f'xdg-open "{file_path}"')
        except Exception as e:
            logger.exception(f"Failed to open file '{file_path_str}'")
            # Fallback using webbrowser if specific openers fail
            try:
                webbrowser.open(f"file://{file_path_str}")
            except Exception as wb_e:
                logger.exception(f"Webbrowser fallback failed for '{file_path_str}'")
                messagebox.showerror(
                    "Error",
                    f"Could not open the file automatically:\n{e}\n\nWebbrowser fallback also failed:\n{wb_e}",
                    parent=self.root,
                )

    def load_history(self) -> dict:
        """Loads the export history from the JSON file."""
        if self.history_file.exists():
            try:
                with self.history_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        logger.info(
                            f"Loaded {len(data)} items from history file: {self.history_file}"
                        )
                        return data
                    else:
                        logger.error(
                            f"History file format error: Expected a dictionary, got {type(data)}. Loading empty history."
                        )
                        return {}
            except json.JSONDecodeError as e:
                logger.error(
                    f"Error decoding history file {self.history_file}: {e}. Loading empty history."
                )
                # Optional: Backup the corrupted file
                # backup_file = self.history_file.with_suffix(".json.corrupted")
                # try:
                #     self.history_file.rename(backup_file)
                #     logger.info(f"Corrupted history file backed up to {backup_file}")
                # except OSError as re:
                #     logger.error(f"Could not backup corrupted history file: {re}")
                return {}
            except Exception:
                logger.exception(
                    f"Failed to load history file {self.history_file}. Loading empty history."
                )
                return {}
        else:
            logger.info("History file not found. Starting with empty history.")
            return {}

    def save_history(self):
        """Saves the current export history to the JSON file."""
        try:
            with self.history_file.open("w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
            logger.debug(f"History saved successfully to {self.history_file}")
        except Exception as e:
            logger.exception(f"Failed to save history file {self.history_file}")
            messagebox.showerror(
                "Error", f"Could not save export history:\n{e}", parent=self.root
            )


# --- Main Execution ---
def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
