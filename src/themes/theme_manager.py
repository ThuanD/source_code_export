import json
import logging
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Dict, Any, Callable


class ThemeManager:
    """Manages application themes (light/dark) and UI customization."""

    # Light theme colors
    LIGHT_THEME = {
        "bg_primary": "#FFFFFF",  # Primary background
        "bg_secondary": "#F0F0F0",  # Secondary background (for panels, etc)
        "bg_tertiary": "#E0E0E0",  # Tertiary background (for headers, etc)
        "fg_primary": "#000000",  # Primary text color
        "fg_secondary": "#555555",  # Secondary text color
        "accent": "#0066CC",  # Accent color for buttons, links, etc
        "accent_hover": "#0055AA",  # Hover state for accent color
        "success": "#4CAF50",  # Success/positive color
        "warning": "#FFC107",  # Warning color
        "error": "#F44336",  # Error/negative color
        "border": "#CCCCCC",  # Border color
    }

    # Dark theme colors
    DARK_THEME = {
        "bg_primary": "#1E1E1E",  # Primary background
        "bg_secondary": "#252525",  # Secondary background (for panels, etc)
        "bg_tertiary": "#333333",  # Tertiary background (for headers, etc)
        "fg_primary": "#FFFFFF",  # Primary text color
        "fg_secondary": "#AAAAAA",  # Secondary text color
        "accent": "#58A6FF",  # Accent color for buttons, links, etc
        "accent_hover": "#79B8FF",  # Hover state for accent color
        "success": "#56D364",  # Success/positive color
        "warning": "#E3B341",  # Warning color
        "error": "#F85149",  # Error/negative color
        "border": "#555555",  # Border color
    }

    def __init__(self, app_data_dir: Path):
        """Initialize theme manager."""
        self.app_data_dir = app_data_dir
        self.settings_file = app_data_dir / "theme_settings.json"
        self.current_theme = "light"  # Default theme
        self.on_theme_change_callbacks = []

        # Load any saved theme settings
        self.load_settings()

    def load_settings(self) -> None:
        """Load theme settings from file."""
        if not self.settings_file.exists():
            logging.info("Theme settings file does not exist. Using default settings.")
            return

        try:
            with self.settings_file.open("r", encoding="utf-8") as f:
                settings = json.load(f)
                self.current_theme = settings.get("theme", "light")
                logging.info(f"Loaded theme settings: {self.current_theme}")
        except Exception as e:
            logging.error(f"Error loading theme settings: {e}")

    def save_settings(self) -> None:
        """Save theme settings to file."""
        try:
            # Make sure the directory exists
            self.app_data_dir.mkdir(parents=True, exist_ok=True)

            settings = {"theme": self.current_theme}
            with self.settings_file.open("w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
                logging.info(f"Saved theme settings: {settings}")
        except Exception as e:
            logging.error(f"Error saving theme settings: {e}")

    def get_current_theme_name(self) -> str:
        """Get the name of the current theme."""
        return self.current_theme

    def get_current_theme_colors(self) -> Dict[str, str]:
        """Get the colors for the current theme."""
        if self.current_theme == "dark":
            return self.DARK_THEME.copy()
        return self.LIGHT_THEME.copy()

    def toggle_theme(self) -> str:
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_settings()
        self._notify_theme_change()
        return self.current_theme

    def set_theme(self, theme_name: str) -> None:
        """Set the theme by name."""
        if theme_name not in ["light", "dark"]:
            logging.warning(f"Unknown theme: {theme_name}. Using default.")
            return

        self.current_theme = theme_name
        self.save_settings()
        self._notify_theme_change()

    def is_dark_theme(self) -> bool:
        """Check if the current theme is dark."""
        return self.current_theme == "dark"

    def register_theme_change_callback(self, callback: Callable) -> None:
        """Register a callback to be called when the theme changes."""
        self.on_theme_change_callbacks.append(callback)

    def _notify_theme_change(self) -> None:
        """Notify all registered callbacks about the theme change."""
        for callback in self.on_theme_change_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Error in theme change callback: {e}")

    def apply_theme_to_ttk(self) -> None:
        """Apply the current theme to ttk widgets."""
        style = ttk.Style()

        colors = self.get_current_theme_colors()

        # Configure ttk theme
        style.theme_use("clam")  # Use clam as base theme

        # Configure common elements
        style.configure(
            ".",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            fieldbackground=colors["bg_primary"],
            troughcolor=colors["bg_tertiary"],
            focuscolor=colors["accent"],
            selectbackground=colors["accent"],
            selectforeground=colors["bg_primary"],
        )

        # Configure TButton
        style.configure(
            "TButton", background=colors["accent"], foreground="white", padding=(10, 5)
        )
        style.map(
            "TButton",
            background=[
                ("active", colors["accent_hover"]),
                ("disabled", colors["bg_tertiary"]),
            ],
            foreground=[("disabled", colors["fg_secondary"])],
        )

        # Configure special buttons
        style.configure("Success.TButton", background=colors["success"])
        style.map(
            "Success.TButton",
            background=[("active", "#45a049")],  # Darker green on hover
        )

        style.configure("Danger.TButton", background=colors["error"])
        style.map(
            "Danger.TButton",
            background=[("active", "#d32f2f")],  # Darker red on hover
        )

        # Configure TFrame
        style.configure("TFrame", background=colors["bg_primary"])
        style.configure("Secondary.TFrame", background=colors["bg_secondary"])
        style.configure("Header.TFrame", background=colors["bg_tertiary"])

        # Configure TLabel
        style.configure("TLabel", background=colors["bg_primary"])
        style.configure(
            "Header.TLabel",
            font=("Arial", 14, "bold"),
            background=colors["bg_tertiary"],
            foreground=colors["accent"],
        )
        style.configure(
            "Title.TLabel",
            font=("Arial", 16, "bold"),
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
        )

        # Configure TEntry
        style.configure(
            "TEntry",
            fieldbackground=colors["bg_primary"],
            foreground=colors["fg_primary"],
            bordercolor=colors["border"],
        )

        # Configure Treeview
        style.configure(
            "Treeview",
            background=colors["bg_primary"],
            fieldbackground=colors["bg_primary"],
            foreground=colors["fg_primary"],
        )
        style.configure(
            "Treeview.Heading",
            background=colors["bg_tertiary"],
            foreground=colors["fg_primary"],
            font=("Arial", 10, "bold"),
        )
        style.map(
            "Treeview",
            background=[("selected", colors["accent"])],
            foreground=[("selected", "white")],
        )

        # Configure TProgressbar
        style.configure(
            "TProgressbar",
            background=colors["accent"],
            troughcolor=colors["bg_tertiary"],
        )

    def apply_theme_to_widget(self, widget: tk.Widget) -> None:
        """Apply the current theme to a specific widget and its children."""
        colors = self.get_current_theme_colors()

        try:
            # Configure the main widget
            if isinstance(widget, (tk.Button, tk.Button)):
                widget.configure(
                    background=colors["accent"],
                    foreground="white",
                    activebackground=colors["accent_hover"],
                    activeforeground="white",
                )
            elif isinstance(widget, (tk.Label, tk.LabelFrame)):
                widget.configure(
                    background=colors["bg_primary"], foreground=colors["fg_primary"]
                )
            elif isinstance(widget, tk.Entry):
                widget.configure(
                    background=colors["bg_primary"],
                    foreground=colors["fg_primary"],
                    insertbackground=colors["fg_primary"],  # Cursor color
                    selectbackground=colors["accent"],
                    selectforeground="white",
                )
            elif isinstance(widget, tk.Text):
                widget.configure(
                    background=colors["bg_primary"],
                    foreground=colors["fg_primary"],
                    insertbackground=colors["fg_primary"],  # Cursor color
                    selectbackground=colors["accent"],
                    selectforeground="white",
                )
            elif isinstance(widget, tk.Frame):
                widget.configure(background=colors["bg_primary"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(
                    background=colors["bg_primary"],
                    foreground=colors["fg_primary"],
                    selectbackground=colors["accent"],
                    selectforeground="white",
                )
            elif isinstance(widget, (tk.Radiobutton, tk.Checkbutton)):
                widget.configure(
                    background=colors["bg_primary"],
                    foreground=colors["fg_primary"],
                    activebackground=colors["bg_primary"],
                    activeforeground=colors["fg_primary"],
                    selectcolor=colors["bg_secondary"],
                )
            elif isinstance(widget, tk.Menu):
                widget.configure(
                    background=colors["bg_primary"],
                    foreground=colors["fg_primary"],
                    activebackground=colors["accent"],
                    activeforeground="white",
                )
        except Exception as e:
            # Log the error but don't crash the application
            logging.warning(
                f"Failed to apply theme to widget {type(widget).__name__}: {e}"
            )

        # Apply to all children recursively
        for child in widget.winfo_children():
            self.apply_theme_to_widget(child)

    def create_themed_widgets(self, parent, **kwargs) -> Dict[str, Any]:
        """Create common widgets with appropriate theme styling."""
        colors = self.get_current_theme_colors()
        widgets = {}

        # Create themed widgets as needed
        if "button" in kwargs:
            widgets["button"] = tk.Button(
                parent,
                text=kwargs.get("button_text", "Button"),
                background=colors["accent"],
                foreground="white",
                activebackground=colors["accent_hover"],
                activeforeground="white",
                relief=tk.FLAT,
                borderwidth=0,
                padx=10,
                pady=5,
                font=("Arial", 10),
            )

        if "label" in kwargs:
            widgets["label"] = tk.Label(
                parent,
                text=kwargs.get("label_text", "Label"),
                background=colors["bg_primary"],
                foreground=colors["fg_primary"],
                font=("Arial", 10),
            )

        if "entry" in kwargs:
            widgets["entry"] = tk.Entry(
                parent,
                background=colors["bg_primary"],
                foreground=colors["fg_primary"],
                insertbackground=colors["fg_primary"],
                selectbackground=colors["accent"],
                selectforeground="white",
                relief=tk.SOLID,
                borderwidth=1,
            )

        if "frame" in kwargs:
            widgets["frame"] = tk.Frame(parent, background=colors["bg_primary"])

        return widgets
