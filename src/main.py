import os
import sys
import logging
import tkinter as tk
from pathlib import Path

from src.controllers.main_controller import MainController


# --- Constants ---
APP_NAME = "Source Code Exporter"
APP_VERSION = "2.0.0"


def get_data_dir() -> Path:
    """Gets a user-writable directory for application data."""
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            data_dir = Path(os.getenv("APPDATA")) / "Source-Code-Export"
        else:
            data_dir = Path.home() / ".source_code_export"
    else:
        # Running as a normal Python script
        data_dir = Path(__file__).parent.parent / "data"

    data_dir.mkdir(exist_ok=True)
    return data_dir


def setup_logging(data_dir: Path) -> None:
    """Set up logging."""
    log_file = data_dir / "app.log"

    # Configure root logger
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up file logging: {e}")

    # Console Handler (for development)
    if not getattr(sys, "frozen", False):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_formatter)
        logger.addHandler(stream_handler)

    logging.info(f"Application started. Version: {APP_VERSION}")
    logging.info(f"Data directory: {data_dir}")
    logging.info(f"Log file: {log_file}")


def create_main_window() -> tk.Tk:
    """Create the main application window."""
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("800x600")

    # Set icon
    if sys.platform == "win32":
        icon_path = Path(__file__).parent.parent / "assets" / "app.ico"
        if icon_path.exists():
            root.iconbitmap(str(icon_path))

    # Make window responsive
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    return root


def main() -> None:
    """Main entry point for the application."""
    # Get data directory
    data_dir = get_data_dir()

    # Set up logging
    setup_logging(data_dir)

    # Create main window
    root = create_main_window()

    # Create and start controller
    MainController(root, data_dir)

    # Start the application
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Uncaught exception")
        try:
            import tkinter.messagebox

            tkinter.messagebox.showerror(
                "Error", f"An unexpected error occurred:\n\n{str(e)}"
            )
        except Exception:
            pass
