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
        "bg_primary": "#FAFBFC",  # Very light blue-gray
        "bg_secondary": "#F6F8FA",  # Light gray-blue
        "bg_tertiary": "#E1ECF4",  # Light blue
        "bg_card": "#FFFFFF",  # Pure white for cards
        "fg_primary": "#24292F",  # Dark gray for primary text
        "fg_secondary": "#656D76",  # Medium gray for secondary text
        "fg_muted": "#8C959F",  # Muted gray for disabled text
        "accent": "#0969DA",  # GitHub blue
        "accent_hover": "#0858B9",  # Darker blue on hover
        "accent_light": "#DDF4FF",  # Very light blue for highlights
        "success": "#2DA44E",  # GitHub green
        "success_hover": "#2C974B",  # Darker green
        "success_light": "#DDF4E8",  # Light green background
        "warning": "#D97706",  # Orange
        "warning_hover": "#B45309",  # Darker orange
        "warning_light": "#FFF8E6",  # Light orange background
        "error": "#CF222E",  # GitHub red
        "error_hover": "#A40E26",  # Darker red
        "error_light": "#FFEBEE",  # Light red background
        "border": "#D0D7DE",  # Light gray border
        "border_focus": "#0969DA",  # Blue border when focused
        "shadow": "#00000010",  # Subtle shadow
    }

    DARK_THEME = {
        "bg_primary": "#0F172A",  # Midnight blue primary
        "bg_secondary": "#1E293B",  # Lighter midnight
        "bg_tertiary": "#334155",  # Medium midnight
        "bg_card": "#1E2A3A",  # Card background
        "fg_primary": "#F8FAFC",  # Pure white text
        "fg_secondary": "#E2E8F0",  # Light gray text
        "fg_muted": "#94A3B8",  # Muted text
        "accent": "#3B82F6",  # Blue accent
        "accent_hover": "#60A5FA",  # Lighter blue
        "accent_light": "#1E3A8A",  # Dark blue highlight
        "success": "#059669",  # Teal success
        "success_hover": "#047857",  # Darker teal
        "success_light": "#022C22",  # Dark teal background
        "warning": "#D97706",  # Orange warning
        "warning_hover": "#B45309",  # Darker orange
        "warning_light": "#3C2412",  # Dark orange background
        "error": "#DC2626",  # Red error
        "error_hover": "#B91C1C",  # Darker red
        "error_light": "#3C1214",  # Dark red background
        "border": "#475569",  # Blue-gray border
        "border_focus": "#3B82F6",  # Blue focus border
        "shadow": "#00000035",  # Medium shadow
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
        """Apply the current theme to ttk widgets with modern styling."""
        style = ttk.Style()

        colors = self.get_current_theme_colors()

        # Configure ttk theme with modern appearance
        style.theme_use("clam")  # Use clam as base theme

        # Configure common elements
        style.configure(
            ".",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            fieldbackground=colors["bg_card"],
            troughcolor=colors["bg_tertiary"],
            focuscolor=colors["accent"],
            selectbackground=colors["accent"],
            selectforeground=colors["bg_card"],
            bordercolor=colors["border"],
            lightcolor=colors["border"],
            darkcolor=colors["border"],
        )

        # Modern TButton with rounded corners and hover effects
        style.configure(
            "TButton",
            background=colors["accent"],
            foreground="white",
            padding=(16, 8),
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "normal"),
        )
        style.map(
            "TButton",
            background=[
                ("active", colors["accent_hover"]),
                ("disabled", colors["bg_tertiary"]),
            ],
            foreground=[("disabled", colors["fg_muted"])],
            relief=[("pressed", "sunken"), ("active", "raised")],
        )

        # Success button style
        style.configure(
            "Success.TButton",
            background=colors["success"],
            foreground="white",
            padding=(16, 8),
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "normal"),
        )
        style.map(
            "Success.TButton",
            background=[
                ("active", colors["success_hover"]),
                ("disabled", colors["bg_tertiary"]),
            ],
            foreground=[("disabled", colors["fg_muted"])],
        )

        # Danger button style
        style.configure(
            "Danger.TButton",
            background=colors["error"],
            foreground="white",
            padding=(16, 8),
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "normal"),
        )
        style.map(
            "Danger.TButton",
            background=[
                ("active", colors["error_hover"]),
                ("disabled", colors["bg_tertiary"]),
            ],
            foreground=[("disabled", colors["fg_muted"])],
        )

        # Warning button style
        style.configure(
            "Warning.TButton",
            background=colors["warning"],
            foreground="white",
            padding=(16, 8),
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "normal"),
        )
        style.map(
            "Warning.TButton",
            background=[
                ("active", colors["warning_hover"]),
                ("disabled", colors["bg_tertiary"]),
            ],
            foreground=[("disabled", colors["fg_muted"])],
        )

        # Modern TFrame styles
        style.configure("TFrame", background=colors["bg_primary"])
        style.configure("Secondary.TFrame", background=colors["bg_secondary"])
        style.configure("Card.TFrame", background=colors["bg_card"])
        style.configure("Header.TFrame", background=colors["bg_tertiary"])

        # Modern TLabel styles
        style.configure("TLabel", background=colors["bg_primary"])
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 14, "bold"),
            background=colors["bg_tertiary"],
            foreground=colors["accent"],
            padding=(8, 4),
        )
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 18, "bold"),
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            padding=(0, 8),
        )
        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 12, "normal"),
            background=colors["bg_primary"],
            foreground=colors["fg_secondary"],
            padding=(0, 4),
        )
        style.configure(
            "Caption.TLabel",
            font=("Segoe UI", 9, "normal"),
            background=colors["bg_primary"],
            foreground=colors["fg_muted"],
            padding=(0, 2),
        )

        # Modern TEntry with focus effects
        style.configure(
            "TEntry",
            fieldbackground=colors["bg_card"],
            foreground=colors["fg_primary"],
            bordercolor=colors["border"],
            focuscolor=colors["border_focus"],
            padding=(8, 6),
            relief="solid",
            borderwidth=1,
        )
        style.map(
            "TEntry",
            bordercolor=[
                ("focus", colors["border_focus"]),
                ("active", colors["accent"]),
            ],
        )

        # Modern Treeview
        style.configure(
            "Treeview",
            background=colors["bg_card"],
            fieldbackground=colors["bg_card"],
            foreground=colors["fg_primary"],
            bordercolor=colors["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "Treeview.Heading",
            background=colors["bg_tertiary"],
            foreground=colors["fg_primary"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", colors["accent"])],
            foreground=[("selected", "white")],
        )
        style.map(
            "Treeview.Heading",
            background=[("active", colors["accent_light"])],
        )

        # Modern TProgressbar
        style.configure(
            "TProgressbar",
            background=colors["accent"],
            troughcolor=colors["bg_tertiary"],
            bordercolor=colors["border"],
            lightcolor=colors["accent"],
            darkcolor=colors["accent"],
            relief="flat",
            borderwidth=0,
        )

        # Modern TNotebook
        style.configure(
            "TNotebook",
            background=colors["bg_primary"],
            bordercolor=colors["border"],
            tabmargins=[2, 5, 2, 0],
        )
        style.configure(
            "TNotebook.Tab",
            background=colors["bg_secondary"],
            foreground=colors["fg_secondary"],
            padding=(12, 6),
            font=("Segoe UI", 10, "normal"),
        )
        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", colors["bg_card"]),
                ("active", colors["accent_light"]),
            ],
            foreground=[
                ("selected", colors["fg_primary"]),
                ("active", colors["accent"]),
            ],
        )

        # Modern TCheckbutton
        style.configure(
            "TCheckbutton",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            font=("Segoe UI", 10, "normal"),
        )

        # Modern TRadiobutton
        style.configure(
            "TRadiobutton",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            font=("Segoe UI", 10, "normal"),
        )

        # Modern TCombobox
        style.configure(
            "TCombobox",
            background=colors["bg_card"],
            foreground=colors["fg_primary"],
            bordercolor=colors["border"],
            focuscolor=colors["border_focus"],
            padding=(8, 6),
            relief="solid",
            borderwidth=1,
        )
        style.map(
            "TCombobox",
            bordercolor=[
                ("focus", colors["border_focus"]),
                ("active", colors["accent"]),
            ],
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
                    relief=tk.FLAT,
                    borderwidth=0,
                    font=("Segoe UI", 10, "normal"),
                    padx=16,
                    pady=8,
                )
            elif isinstance(widget, (tk.Label, tk.LabelFrame)):
                widget.configure(
                    background=colors["bg_primary"],
                    foreground=colors["fg_primary"],
                    font=("Segoe UI", 10, "normal"),
                )
            elif isinstance(widget, tk.Entry) and not isinstance(widget, ttk.Entry):
                widget.configure(
                    background=colors["bg_card"],
                    foreground=colors["fg_primary"],
                    insertbackground=colors["fg_primary"],
                    selectbackground=colors["accent"],
                    selectforeground="white",
                    relief=tk.SOLID,
                    borderwidth=1,
                    font=("Segoe UI", 10, "normal"),
                )
            elif isinstance(widget, tk.Text):
                widget.configure(
                    background=colors["bg_card"],
                    foreground=colors["fg_primary"],
                    insertbackground=colors["fg_primary"],
                    selectbackground=colors["accent"],
                    selectforeground="white",
                    relief=tk.SOLID,
                    borderwidth=1,
                    font=("Segoe UI", 10, "normal"),
                )
            elif isinstance(widget, tk.Frame):
                widget.configure(background=colors["bg_primary"])
            elif isinstance(widget, tk.Canvas):
                widget.configure(background=colors["bg_primary"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(
                    background=colors["bg_card"],
                    foreground=colors["fg_primary"],
                    selectbackground=colors["accent"],
                    selectforeground="white",
                    relief=tk.SOLID,
                    borderwidth=1,
                    font=("Segoe UI", 10, "normal"),
                )
            elif isinstance(widget, (tk.Radiobutton, tk.Checkbutton)):
                widget.configure(
                    background=colors["bg_primary"],
                    foreground=colors["fg_primary"],
                    activebackground=colors["bg_primary"],
                    activeforeground=colors["fg_primary"],
                    selectcolor=colors["bg_secondary"],
                    font=("Segoe UI", 10, "normal"),
                )
            elif isinstance(widget, tk.Menu):
                widget.configure(
                    background=colors["bg_card"],
                    foreground=colors["fg_primary"],
                    activebackground=colors["accent"],
                    activeforeground="white",
                    relief=tk.SOLID,
                    borderwidth=1,
                    font=("Segoe UI", 10, "normal"),
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
                padx=16,
                pady=8,
                font=("Segoe UI", 10, "normal"),
            )

        if "label" in kwargs:
            widgets["label"] = tk.Label(
                parent,
                text=kwargs.get("label_text", "Label"),
                background=colors["bg_primary"],
                foreground=colors["fg_primary"],
                font=("Segoe UI", 10, "normal"),
            )

        if "entry" in kwargs:
            widgets["entry"] = tk.Entry(
                parent,
                background=colors["bg_card"],
                foreground=colors["fg_primary"],
                insertbackground=colors["fg_primary"],
                selectbackground=colors["accent"],
                selectforeground="white",
                relief=tk.SOLID,
                borderwidth=1,
                font=("Segoe UI", 10, "normal"),
            )

        if "frame" in kwargs:
            widgets["frame"] = tk.Frame(parent, background=colors["bg_primary"])

        return widgets
