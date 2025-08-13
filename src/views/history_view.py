import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from typing import Dict, Any, List, Callable

from src.views.base_view import BaseView


class HistoryView(BaseView):
    """View for displaying and managing export history."""

    def __init__(self, *args, **kwargs):
        """Initialize the history view."""
        super().__init__(*args, **kwargs)
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="last_run")
        self.sort_order_var = tk.BooleanVar(value=True)  # True for descending

    def create_widgets(self) -> None:
        """Create the history view widgets."""
        self.frame = self.create_card_frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Title
        title_frame = self.create_themed_frame(self.frame)
        title_frame.pack(fill=tk.X, pady=(0, 16))

        title_label = self.create_title_label(
            title_frame, self._("export_history")
        )
        title_label.pack(side=tk.LEFT, pady=8)
        logging.debug(f"Created title label with text: {self._('export_history')}")

        # Control buttons frame
        control_buttons_frame = self.create_themed_frame(title_frame)
        control_buttons_frame.pack(side=tk.RIGHT)

        # Add theme toggle button
        theme_button = self.create_themed_button(
            control_buttons_frame,
            text=self._("dark_theme")
            if not self.theme_manager.is_dark_theme()
            else self._("light_theme"),
            command=self._toggle_theme,
        )
        theme_button.pack(side=tk.LEFT, padx=(0, 8))
        self.widgets["theme_button"] = theme_button

        # Add language toggle button
        lang_button = self.create_themed_button(
            control_buttons_frame,
            text="English"
            if self.language_manager.get_current_language() == "vi"
            else "Tiếng Việt",
            command=self._toggle_language,
        )
        lang_button.pack(side=tk.LEFT)
        self.widgets["lang_button"] = lang_button

        # Action buttons
        action_buttons_frame = self.create_themed_frame(self.frame)
        action_buttons_frame.pack(fill=tk.X, pady=(0, 16))

        buttons = [
            {"text": self._("new_export"), "command": self._on_new_export, "style": "Success.TButton"},
            {"text": self._("delete_selected"), "command": self._on_delete_selected, "style": "Danger.TButton"},
            {"text": self._("settings"), "command": self._on_settings, "style": "TButton"},
        ]
        self.create_button_group(action_buttons_frame, buttons)

        # History list section
        history_section = self.create_titled_section(self.frame, "")
        history_section["frame"].pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with modern styling
        tree_frame = self.create_themed_frame(history_section["content"])
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("project_path", "last_run", "run_count", "created"),
            show="tree headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Configure treeview columns
        self.tree.heading("#0", text="")
        self.tree.column("#0", width=0, stretch=tk.NO)

        self.tree.heading("project_path", text=self._("project_path"))
        self.tree.column("project_path", width=300, minwidth=200)

        self.tree.heading("last_run", text=self._("last_run"))
        self.tree.column("last_run", width=150, minwidth=120)

        self.tree.heading("run_count", text=self._("run_count", "Run Count"))
        self.tree.column("run_count", width=80, minwidth=60)

        self.tree.heading("created", text=self._("created", "Created"))
        self.tree.column("created", width=150, minwidth=120)

        # Bind double-click event
        self.tree.bind("<Double-1>", self._on_item_double_click)


    def populate_tree(self, items: List[Dict[str, Any]]) -> None:
        """Populate the tree with history items."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add new items
        for item in items:
            path = item.get("path", "")

            # Format the last run timestamp
            last_run_ts = item.get("last_run", 0)
            if last_run_ts:
                try:
                    last_run_str = item.get(
                        "last_run_formatted",
                        datetime.fromtimestamp(last_run_ts).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    )
                except Exception:
                    logging.warning(f"Invalid timestamp for {path}: {last_run_ts}")
                    last_run_str = self._("unknown", "Unknown")
            else:
                last_run_str = self._("never", "Never")

            # Get run count
            run_count = item.get("run_count", 1)

            # Get created date
            created_ts = item.get("created", 0)
            if created_ts:
                try:
                    created_str = item.get(
                        "created_formatted",
                        datetime.fromtimestamp(created_ts).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    )
                except Exception:
                    created_str = self._("unknown", "Unknown")
            else:
                created_str = self._("unknown", "Unknown")

            # Insert into tree
            self.tree.insert(
                "",
                "end",
                values=(path, last_run_str, run_count, created_str),
                tags=(path,),
            )

        # Apply alternating row colors
        for i, item in enumerate(self.tree.get_children()):
            if i % 2 == 0:
                self.tree.item(item, tags=("even",))
            else:
                self.tree.item(item, tags=("odd",))

        # Apply tag configurations
        colors = self.theme_manager.get_current_theme_colors()
        self.tree.tag_configure("even", background=colors["bg_primary"])
        self.tree.tag_configure("odd", background=colors["bg_secondary"])

    def set_callbacks(
        self,
        on_new_export: Callable = None,
        on_open_export: Callable = None,
        on_delete_exports: Callable = None,
        on_settings: Callable = None,
    ) -> None:
        """Set callbacks for user actions."""
        self._on_new_export_callback = on_new_export
        self._on_open_export_callback = on_open_export
        self._on_delete_exports_callback = on_delete_exports
        self._on_settings_callback = on_settings

    def get_selected_items(self) -> List[str]:
        """Get the paths of selected items."""
        selected = []
        for item_id in self.tree.selection():
            values = self.tree.item(item_id, "values")
            if values and len(values) > 0:
                selected.append(values[0])  # Path is the first column

        return selected

    def on_theme_change(self) -> None:
        """Handle theme changes."""
        super().on_theme_change()

        # Update theme button text
        if "theme_button" in self.widgets:
            self.widgets["theme_button"].configure(
                text=self._("dark_theme")
                if not self.theme_manager.is_dark_theme()
                else self._("light_theme")
            )

        # Apply tag configurations
        if hasattr(self, "tree"):
            colors = self.theme_manager.get_current_theme_colors()
            self.tree.tag_configure("even", background=colors["bg_primary"])
            self.tree.tag_configure("odd", background=colors["bg_secondary"])

    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self.theme_manager.toggle_theme()

    def _toggle_language(self) -> None:
        """Toggle between languages."""
        current = self.language_manager.get_current_language()
        new_lang = "vi" if current == "en" else "en"
        logging.debug(f"Toggling language from {current} to {new_lang}")

        self.language_manager.change_language(new_lang)

        # Debug translations
        self.language_manager.debug_translations()

        # Update language button text
        if "lang_button" in self.widgets:
            self.widgets["lang_button"].configure(
                text="English" if new_lang == "vi" else "Tiếng Việt"
            )

        # Refresh view to update all translations
        self._refresh_view()

        # Also refresh export view if it exists and is visible
        if (
            hasattr(self, "controller")
            and self.controller
            and self.controller.export_view
        ):
            self.controller.export_view.refresh_translations()

    def _refresh_view(self) -> None:
        """Refresh the view to update translations."""
        logging.debug("Starting _refresh_view()")

        # Temporarily store any state that needs to be preserved
        selected = self.get_selected_items()
        logging.debug(f"Preserved selected items: {selected}")

        # Destroy and recreate widgets
        self.destroy()
        logging.debug("Widgets destroyed, recreating...")
        self.create_widgets()
        logging.debug("Widgets recreated")

        # Re-register callbacks after recreation
        if hasattr(self, "_on_new_export_callback"):
            self.widgets["new_export_button"].configure(command=self._on_new_export)
        if hasattr(self, "_on_delete_exports_callback"):
            self.widgets["delete_button"].configure(command=self._on_delete_selected)
        if hasattr(self, "_on_settings_callback"):
            self.widgets["settings_button"].configure(command=self._on_settings)

        # Restore state if needed and request data refresh
        if hasattr(self, "_on_filter_callback"):
            self._on_filter_callback(
                self.search_var.get(), self.sort_var.get(), self.sort_order_var.get()
            )
        elif hasattr(self, "controller") and self.controller:
            # If filter callback is not set, call controller directly
            self.controller.on_filter_history(
                self.search_var.get(), self.sort_var.get(), self.sort_order_var.get()
            )

    def _on_search_changed(self, event) -> None:
        """Handle search text changes."""
        if hasattr(self, "_on_filter_callback"):
            self._on_filter_callback(
                self.search_var.get(), self.sort_var.get(), self.sort_order_var.get()
            )

    def _on_sort_changed(self, event) -> None:
        """Handle sort selection changes."""
        if hasattr(self, "_on_filter_callback"):
            self._on_filter_callback(
                self.search_var.get(), self.sort_var.get(), self.sort_order_var.get()
            )

    def _toggle_sort_order(self) -> None:
        """Toggle sort order between ascending and descending."""
        self.sort_order_var.set(not self.sort_order_var.get())

        # Update button text
        self.widgets["sort_order_button"].configure(
            text="↓" if self.sort_order_var.get() else "↑"
        )

        # Refresh data
        if hasattr(self, "_on_filter_callback"):
            self._on_filter_callback(
                self.search_var.get(), self.sort_var.get(), self.sort_order_var.get()
            )

    def _on_item_double_click(self, event) -> None:
        """Handle double click on an item."""
        if (
            not hasattr(self, "_on_open_export_callback")
            or not self._on_open_export_callback
        ):
            return

        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item, "values")

        if values and len(values) > 0:
            self._on_open_export_callback(values[0])  # Path is the first column

    def _on_new_export(self) -> None:
        """Handle new export button click."""
        if hasattr(self, "_on_new_export_callback") and self._on_new_export_callback:
            self._on_new_export_callback()

    def _on_delete_selected(self) -> None:
        """Handle delete selected button click."""
        if (
            not hasattr(self, "_on_delete_exports_callback")
            or not self._on_delete_exports_callback
        ):
            return

        selected = self.get_selected_items()
        if not selected:
            messagebox.showinfo(
                self._("info"), self._("no_items_selected"), parent=self.parent
            )
            return

        # Confirm deletion
        if messagebox.askyesno(
            self._("warning"),
            self._("confirm_delete", None, len(selected)),
            parent=self.parent,
        ):
            self._on_delete_exports_callback(selected)

    def _on_settings(self) -> None:
        """Handle settings button click."""
        if hasattr(self, "_on_settings_callback") and self._on_settings_callback:
            self._on_settings_callback()
