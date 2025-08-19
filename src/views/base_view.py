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
        self.frame = ttk.Frame(self.parent, style="Card.TFrame")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

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
            self.frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

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

    def create_card_frame(self, parent: tk.Widget, **kwargs) -> ttk.Frame:
        """Create a card-style frame with modern styling."""
        frame = self.create_themed_frame(parent, style="Card.TFrame", **kwargs)
        return frame

    def create_section_header(self, parent: tk.Widget, text: str) -> ttk.Label:
        """Create a section header label."""
        return self.create_themed_label(parent, text, style="Header.TLabel")

    def create_title_label(self, parent: tk.Widget, text: str) -> ttk.Label:
        """Create a title label."""
        return self.create_themed_label(parent, text, style="Title.TLabel")

    def create_subtitle_label(self, parent: tk.Widget, text: str) -> ttk.Label:
        """Create a subtitle label."""
        return self.create_themed_label(parent, text, style="Subtitle.TLabel")

    def create_caption_label(self, parent: tk.Widget, text: str) -> ttk.Label:
        """Create a caption label."""
        return self.create_themed_label(parent, text, style="Caption.TLabel")

    def create_titled_section(self, parent: tk.Widget, title: str) -> Dict[str, Any]:
        """Create a titled section with a header and content frame."""
        section = {}
        section["frame"] = self.create_card_frame(parent)
        section["header"] = self.create_section_header(section["frame"], title)
        section["header"].pack(fill=tk.X, pady=(12, 8), padx=12)
        section["content"] = self.create_themed_frame(section["frame"])
        section["content"].pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        return section

    def create_form_field(
        self, parent: tk.Widget, label_text: str, widget_type: str = "entry", **kwargs
    ) -> Dict[str, Any]:
        """Create a form field with label and input widget."""
        field = {}

        # Create container frame
        field["container"] = self.create_themed_frame(parent)
        field["container"].pack(fill=tk.X, pady=4)

        # Create label
        field["label"] = self.create_themed_label(field["container"], label_text)
        field["label"].pack(anchor=tk.W, pady=(0, 4))

        # Create input widget based on type
        if widget_type == "entry":
            field["widget"] = self.create_themed_entry(field["container"], **kwargs)
        elif widget_type == "combobox":
            field["widget"] = ttk.Combobox(field["container"], **kwargs)
        elif widget_type == "text":
            field["widget"] = tk.Text(field["container"], height=4, **kwargs)
        elif widget_type == "checkbox":
            field["widget"] = ttk.Checkbutton(
                field["container"], text=label_text, **kwargs
            )
            field["label"].pack_forget()  # Hide label for checkbox
        elif widget_type == "radiobutton":
            field["widget"] = ttk.Radiobutton(
                field["container"], text=label_text, **kwargs
            )
            field["label"].pack_forget()  # Hide label for radiobutton

        field["widget"].pack(fill=tk.X)

        return field

    def create_button_group(self, parent: tk.Widget, buttons: list) -> ttk.Frame:
        """Create a group of buttons with consistent spacing."""
        button_frame = self.create_themed_frame(parent)
        button_frame.pack(fill=tk.X, pady=8)

        for i, button_config in enumerate(buttons):
            text = button_config.get("text", "")
            command = button_config.get("command")
            style = button_config.get("style", "TButton")

            button = self.create_themed_button(
                button_frame, text=text, command=command, style=style
            )

            if i == 0:
                button.pack(side=tk.LEFT)
            else:
                button.pack(side=tk.LEFT, padx=(8, 0))

        return button_frame

    def create_info_card(
        self, parent: tk.Widget, title: str, content: str, icon: str = "ℹ"
    ) -> ttk.Frame:
        """Create an info card with title, content and optional icon."""
        card = self.create_card_frame(parent)
        card.pack(fill=tk.X, pady=8)

        # Header with icon and title
        header_frame = self.create_themed_frame(card)
        header_frame.pack(fill=tk.X, padx=12, pady=(12, 8))

        icon_label = self.create_themed_label(header_frame, icon, style="Title.TLabel")
        icon_label.pack(side=tk.LEFT, padx=(0, 8))

        title_label = self.create_title_label(header_frame, title)
        title_label.pack(side=tk.LEFT)

        # Content
        content_label = self.create_subtitle_label(card, content)
        content_label.pack(anchor=tk.W, padx=12, pady=(0, 12))

        return card

    def create_status_bar(self, parent: tk.Widget) -> Dict[str, Any]:
        """Create a modern status bar."""
        status_frame = self.create_themed_frame(parent, style="Secondary.TFrame")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))

        status = {}
        status["frame"] = status_frame
        status["label"] = self.create_caption_label(status_frame, "")
        status["label"].pack(side=tk.LEFT, padx=8, pady=4)

        return status

    def create_progress_section(self, parent: tk.Widget) -> Dict[str, Any]:
        """Create a progress section with bar and status."""
        progress_frame = self.create_card_frame(parent)
        progress_frame.pack(fill=tk.X, pady=8)

        progress = {}
        progress["frame"] = progress_frame

        # Progress label
        progress["label"] = self.create_subtitle_label(progress_frame, "")
        progress["label"].pack(anchor=tk.W, padx=12, pady=(12, 8))

        # Progress bar
        progress["bar"] = ttk.Progressbar(
            progress_frame, orient=tk.HORIZONTAL, mode="determinate", length=200
        )
        progress["bar"].pack(fill=tk.X, padx=12, pady=(0, 8))

        # Status label
        progress["status"] = self.create_caption_label(progress_frame, "")
        progress["status"].pack(anchor=tk.W, padx=12, pady=(0, 12))

        return progress
