import logging
import tkinter as tk
import queue
import threading
import webbrowser
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import tkinter.messagebox as messagebox

from src.models.exporter import SourceCodeExporter
from src.models.history import ExportHistory
from src.themes.theme_manager import ThemeManager
from src.i18n.language_manager import LanguageManager
from src.views.history_view import HistoryView
from src.views.export_view import ExportView


class MainController:
    """Main controller for the application."""

    def __init__(self, root: tk.Tk, app_data_dir: Path):
        """Initialize the main controller."""
        self.root = root
        self.app_data_dir = app_data_dir
        self.export_queue = queue.Queue()
        self.current_path = None  # Current export path being edited

        # Initialize managers
        self.theme_manager = ThemeManager(app_data_dir)
        self.language_manager = LanguageManager(app_data_dir)
        self.history_manager = ExportHistory(app_data_dir / "export_history.json")

        # Initialize views
        self.history_view = None
        self.export_view = None

        # Apply theme to ttk widgets
        self.theme_manager.apply_theme_to_ttk()

        # Apply theme to the root window and register for changes
        self._update_root_theme()
        self.theme_manager.register_theme_change_callback(self._update_root_theme)

        # Create initial view
        self._create_history_view()

    def _create_history_view(self) -> None:
        """Create and show the history view."""
        # Hide export view if it exists
        if self.export_view:
            self.export_view.hide()

        # Create history view if needed
        if not self.history_view:
            self.history_view = HistoryView(
                self.root, self.theme_manager, self.language_manager, controller=self
            )

            # Set callbacks
            self.history_view.set_callbacks(
                on_new_export=self.on_new_export,
                on_open_export=self.on_open_export,
                on_delete_exports=self.on_delete_exports,
                on_settings=self.on_settings,
            )

            # Register filter callback
            self.history_view._on_filter_callback = self.on_filter_history

            # Initialize view
            self.history_view.initialize()
        else:
            self.history_view.show()

        # Populate history
        self._refresh_history()

    def _create_export_view(self) -> None:
        """Create and show the export view."""
        # Hide history view if it exists
        if self.history_view:
            self.history_view.hide()

        # Create export view if needed
        if not self.export_view:
            self.export_view = ExportView(
                self.root, self.theme_manager, self.language_manager, controller=self
            )

            # Set callbacks
            self.export_view.set_callbacks(
                on_back=self.on_back_to_history,
                on_delete_config=self.on_delete_current_config,
                on_run_export=self.on_run_export,
            )

            # Initialize view
            self.export_view.initialize()
        else:
            self.export_view.show()

    def _refresh_history(
        self, search_query="", sort_by="last_run", sort_desc=True
    ) -> None:
        """Refresh the history view."""
        if not self.history_view:
            return

        # Get sorted entries
        if search_query:
            entries = self.history_manager.search_entries(search_query)
        else:
            entries = self.history_manager.get_sorted_entries(sort_by, sort_desc)

        # Populate tree
        self.history_view.populate_tree(entries)

    def on_filter_history(
        self, search_query: str, sort_by: str, sort_desc: bool
    ) -> None:
        """Handle history filter changes."""
        self._refresh_history(search_query, sort_by, sort_desc)

    def on_new_export(self) -> None:
        """Handle new export action."""
        self.current_path = None
        self._create_export_view()

        # Set default values
        default_config = {
            "input_folder": "",
            "output_file": "",
            "exclude_paths": [],
            "exclude_extensions": [],
            "output_format": "txt",
            "exclude_size_above": 0,
        }

        self.export_view.set_values(default_config)

    def on_open_export(self, path: str) -> None:
        """Handle open export action."""
        self.current_path = path
        config = self.history_manager.get_entry(path)

        if not config:
            logging.error(f"Config not found for path: {path}")
            return

        self._create_export_view()
        self.export_view.set_values(config)

    def on_delete_exports(self, paths: List[str]) -> None:
        """Handle delete exports action."""
        if not paths:
            return

        count = self.history_manager.delete_entries(paths)
        logging.info(f"Deleted {count} history entries")

        # Refresh history view
        self._refresh_history()

    def on_delete_current_config(self) -> None:
        """Handle delete current config action."""
        if not self.current_path:
            return

        if self.history_manager.delete_entry(self.current_path):
            logging.info(f"Deleted history entry: {self.current_path}")
            self.current_path = None

            # Go back to history view
            self._create_history_view()

    def on_back_to_history(self) -> None:
        """Handle back to history action."""
        self._create_history_view()

    def on_settings(self) -> None:
        """Handle settings action."""
        # TODO: Implement proper settings dialog
        # For now, show a placeholder message
        import tkinter.messagebox as messagebox

        messagebox.showinfo(
            "Settings",
            "Settings dialog will be implemented in future versions.\n\n"
            "For now, use the theme toggle button in the top-right corner to change themes.",
            parent=self.root,
        )

    def on_run_export(self, config: Dict[str, Any]) -> None:
        """Handle run export action."""
        # Make sure we have a path
        path = config.get("input_folder", "")
        if not path:
            return

        # Update current path
        self.current_path = path

        # Save to history first
        self.history_manager.add_entry(path, config)

        # Disable run button
        self.export_view.set_running_state(True)

        # Reset progress
        self.export_view.update_progress(0, self.language_manager.get_text("preparing"))

        # Run in a separate thread
        export_thread = threading.Thread(
            target=self._perform_export_thread, args=(config, self.export_queue)
        )
        export_thread.daemon = True
        export_thread.start()

        # Start checking for results
        self.root.after(100, self._check_export_status)

    def _perform_export_thread(self, params: Dict[str, Any], q: queue.Queue) -> None:
        """Perform the export in a separate thread."""
        try:
            input_folder = params.get("input_folder", "")
            output_file = params.get("output_file", "")
            exclude_paths = params.get("exclude_paths", [])
            exclude_extensions = params.get("exclude_extensions", [])
            output_format = params.get("output_format", "txt")
            exclude_size = params.get("exclude_size_above", 0)

            if not input_folder or not output_file:
                q.put({"status": "error", "message": "Invalid input parameters"})
                return

            # Initialize exporter
            exporter = SourceCodeExporter(
                input_folder,
                exclude_paths=exclude_paths,
                exclude_extensions=exclude_extensions,
                exclude_size_above=exclude_size,
                output_format=output_format,
            )

            # Count items (this will update stats)
            q.put(
                {
                    "status": "progress",
                    "progress": 0.1,
                    "message": self.language_manager.get_text("analyzing"),
                }
            )
            exporter.count_items()

            # Register a progress callback
            def progress_callback():
                current, total, current_file = exporter.get_progress()
                if total > 0:
                    progress = min(0.1 + 0.9 * (current / total), 0.99)
                    message = self.language_manager.get_text(
                        "processing_file", None, current_file or ""
                    )
                    q.put(
                        {"status": "progress", "progress": progress, "message": message}
                    )
                return True

            # Set up a timer to check progress
            progress_timer = None

            def check_progress():
                if progress_callback():
                    # Schedule next check
                    nonlocal progress_timer
                    progress_timer = threading.Timer(0.1, check_progress)
                    progress_timer.daemon = True
                    progress_timer.start()

            # Start progress monitoring
            check_progress()

            # Export the structure
            q.put(
                {
                    "status": "progress",
                    "progress": 0.2,
                    "message": self.language_manager.get_text("exporting"),
                }
            )

            stats = exporter.export_structure(Path(output_file))

            # Cancel the timer
            if progress_timer:
                progress_timer.cancel()

            # Update history with stats
            if self.current_path:
                self.history_manager.update_stats(self.current_path, stats)

            # Success
            q.put(
                {
                    "status": "complete",
                    "output_file": output_file,
                    "stats": stats,
                }
            )
        except Exception as e:
            logging.exception("Error in export thread")
            q.put({"status": "error", "message": str(e)})

    def _check_export_status(self) -> None:
        """Check for export status updates."""
        try:
            # Check for message in queue
            message = self.export_queue.get_nowait()

            status = message.get("status")

            if status == "progress":
                # Update progress
                progress = message.get("progress", 0)
                status_text = message.get("message", "")
                self.export_view.update_progress(progress, status_text)

                # Check again soon
                self.root.after(100, self._check_export_status)
            elif status == "complete":
                # Export complete
                self.export_view.update_progress(
                    1.0, self.language_manager.get_text("export_complete")
                )
                self.export_view.set_running_state(False)

            elif status == "error":
                # Export failed
                error_message = message.get("message", "Unknown error")
                self.export_view.update_progress(
                    0, self.language_manager.get_text("export_failed")
                )
                self.export_view.set_running_state(False)

                # Show error dialog
                tk.messagebox.showerror(
                    self.language_manager.get_text("error"),
                    f"{self.language_manager.get_text('export_failed')}: {error_message}",
                    parent=self.root,
                )
        except queue.Empty:
            # No messages, check again soon
            self.root.after(100, self._check_export_status)
        except Exception:
            logging.exception("Error checking export status")
            self.export_view.set_running_state(False)

    def _copy_stats_to_clipboard(self, stats: Dict[str, Any], output_file: str) -> None:
        """Copy export statistics to clipboard."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Format stats as text
            stats_text = self.language_manager.get_text("stats_title") + "\n"
            stats_text += "=" * 40 + "\n\n"

            stats_text += (
                f"{self.language_manager.get_text('timestamp')}: {timestamp}\n"
            )
            stats_text += (
                f"{self.language_manager.get_text('output_path')}: {output_file}\n\n"
            )

            # Basic stats
            basic_stats = [
                ("total_dirs", stats.get("total_dirs", 0)),
                ("total_files", stats.get("total_files", 0)),
                ("total_size", self._format_size(stats.get("total_size", 0))),
                ("exported_files", stats.get("exported_files", 0)),
                ("exported_size", self._format_size(stats.get("exported_size", 0))),
                ("skipped_files", stats.get("skipped_files", 0)),
            ]

            for key, value in basic_stats:
                stats_text += f"{self.language_manager.get_text(key)}: {value}\n"

            # File types
            file_types = stats.get("file_types", {})
            if file_types:
                stats_text += f"\n{self.language_manager.get_text('file_types')}:\n"
                stats_text += "-" * 40 + "\n"

                total_files = stats.get("total_files", 0)
                sorted_types = sorted(
                    file_types.items(), key=lambda x: x[1], reverse=True
                )

                for ext, count in sorted_types[:10]:  # Top 10 file types
                    percentage = (count / total_files * 100) if total_files > 0 else 0
                    stats_text += f"{ext}: {count} ({percentage:.1f}%)\n"

                if len(sorted_types) > 10:
                    stats_text += f"... {len(sorted_types) - 10} more file types\n"

            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(stats_text)

            # Show success message
            messagebox.showinfo(
                self.language_manager.get_text("success"),
                self.language_manager.get_text(
                    "stats_copied", "Statistics copied to clipboard"
                ),
                parent=self.root,
            )
        except Exception as e:
            logging.error(f"Error copying stats to clipboard: {e}")
            messagebox.showerror(
                self.language_manager.get_text("error"),
                f"{self.language_manager.get_text('copy_failed', 'Failed to copy statistics')}: {str(e)}",
                parent=self.root,
            )

    def _open_output_file(self, output_file: str) -> None:
        """Open the output file in the default application."""
        try:
            output_path = Path(output_file)
            if output_path.exists():
                webbrowser.open(output_file)
            else:
                tk.messagebox.showwarning(
                    self.language_manager.get_text("warning"),
                    self.language_manager.get_text("file_not_found", "File not found."),
                    parent=self.root,
                )
        except Exception as e:
            logging.error(f"Error opening output file: {e}")
            tk.messagebox.showerror(
                self.language_manager.get_text("error"), str(e), parent=self.root
            )

    def _format_size(self, size_bytes: int) -> str:
        """Format a byte size into a human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024 or unit == "GB":
                if unit == "B":
                    return f"{size_bytes} {unit}"
                return f"{size_bytes / 1024:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"  # Should never reach here for code projects

    def _update_root_theme(self) -> None:
        """Apply the current theme to the root window."""
        colors = self.theme_manager.get_current_theme_colors()
        self.root.configure(background=colors["bg_primary"])
