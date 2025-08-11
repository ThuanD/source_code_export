import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable

from src.themes.theme_manager import ThemeManager
from src.i18n.language_manager import LanguageManager


class BaseView:
    """Base class for all application views."""

    def __init__(
        self,
        parent: tk.Widget,
        theme_manager: ThemeManager,
        language_manager: LanguageManager,
        controller: Any = None,
    ):
        """Initialize the base view."""
        self.parent = parent
        self.theme_manager = theme_manager
        self.language_manager = language_manager
        self.controller = controller
        self.frame = None
        self.widgets = {}

        # Register for theme changes
        self.theme_manager.register_theme_change_callback(self.on_theme_change)

    def initialize(self) -> None:
        """Initialize the view."""
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create the view's widgets."""
        # This method should be overridden by subclasses
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

    def destroy(self) -> None:
        """Destroy the view's widgets."""
        if self.frame:
            self.frame.destroy()
            self.frame = None

    def hide(self) -> None:
        """Hide the view."""
        if self.frame:
            self.frame.pack_forget()

    def show(self) -> None:
        """Show the view."""
        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)

    def on_theme_change(self) -> None:
        """Handle theme changes."""
        # Apply theme to ttk widgets
        self.theme_manager.apply_theme_to_ttk()

        # Apply theme to any custom widgets
        if self.frame:
            self.theme_manager.apply_theme_to_widget(self.frame)

    def _(self, key: str, default: Optional[str] = None, *args) -> str:
        """Shorthand for getting translated text."""
        return self.language_manager.get_text(key, default, *args)

    def create_themed_label(self, parent: tk.Widget, text: str, **kwargs) -> ttk.Label:
        """Create a themed label."""
        style = kwargs.pop("style", "TLabel")
        label = ttk.Label(parent, text=text, style=style, **kwargs)
        return label

    def create_themed_button(
        self, parent: tk.Widget, text: str, command: Callable = None, **kwargs
    ) -> ttk.Button:
        """Create a themed button."""
        style = kwargs.pop("style", "TButton")
        button = ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        return button

    def create_themed_entry(self, parent: tk.Widget, **kwargs) -> ttk.Entry:
        """Create a themed entry widget."""
        entry = ttk.Entry(parent, **kwargs)
        return entry

    def create_themed_frame(self, parent: tk.Widget, **kwargs) -> ttk.Frame:
        """Create a themed frame."""
        style = kwargs.pop("style", "TFrame")
        frame = ttk.Frame(parent, style=style, **kwargs)
        return frame

    def create_section_header(self, parent: tk.Widget, text: str) -> ttk.Label:
        """Create a section header label."""
        return self.create_themed_label(parent, text, style="Header.TLabel")

    def create_titled_section(self, parent: tk.Widget, title: str) -> Dict[str, Any]:
        """Create a titled section with a header and content frame."""
        section = {}
        section["frame"] = self.create_themed_frame(parent)
        section["header"] = self.create_section_header(section["frame"], title)
        section["header"].pack(fill=tk.X, pady=(10, 5))
        section["content"] = self.create_themed_frame(section["frame"])
        section["content"].pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return section
