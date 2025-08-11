import json
import logging
from pathlib import Path
from typing import Dict, Optional


class LanguageManager:
    """Manages application internationalization (i18n)."""

    # Available languages
    AVAILABLE_LANGUAGES = {
        "en": "English",
        "vi": "Tiếng Việt",
    }

    def __init__(self, app_data_dir: Path):
        """Initialize language manager."""
        self.app_data_dir = app_data_dir
        self.settings_file = app_data_dir / "language_settings.json"
        self.language_dir = Path(__file__).parent
        self.current_language = "en"  # Default language
        self.translations = {}

        # Load settings and translations
        self.load_settings()
        self.load_translations()

    def load_settings(self) -> None:
        """Load language settings from file."""
        if not self.settings_file.exists():
            logging.info(
                "Language settings file does not exist. Using default language."
            )
            return

        try:
            with self.settings_file.open("r", encoding="utf-8") as f:
                settings = json.load(f)
                language = settings.get("language", "en")
                if language in self.AVAILABLE_LANGUAGES:
                    self.current_language = language
                    logging.info(f"Loaded language setting: {language}")
                else:
                    logging.warning(f"Unknown language: {language}. Using default.")
        except Exception as e:
            logging.error(f"Error loading language settings: {e}")

    def save_settings(self) -> None:
        """Save language settings to file."""
        try:
            # Make sure the directory exists
            self.app_data_dir.mkdir(parents=True, exist_ok=True)

            settings = {"language": self.current_language}
            with self.settings_file.open("w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
                logging.info(f"Saved language setting: {self.current_language}")
        except Exception as e:
            logging.error(f"Error saving language settings: {e}")

    def load_translations(self) -> None:
        """Load translations for the current language."""
        language_file = self.language_dir / f"{self.current_language}.json"

        # First try to load from language_file
        if language_file.exists():
            try:
                with language_file.open("r", encoding="utf-8") as f:
                    self.translations = json.load(f)
                    logging.info(f"Loaded translations from {language_file}")
                    return
            except Exception as e:
                logging.error(f"Error loading translations from {language_file}: {e}")

        # If that fails, load from embedded translations
        self.translations = self._get_embedded_translations()
        logging.info(f"Using embedded translations for {self.current_language}")

        # Debug: Log some sample translations
        current_translations = self.translations.get(self.current_language, {})
        logging.debug(f"Current language: {self.current_language}")
        logging.debug(f"Sample translations: {list(current_translations.keys())[:5]}")
        logging.debug(
            f"'new_export' translation: {current_translations.get('new_export', 'NOT FOUND')}"
        )

    def _get_embedded_translations(self) -> Dict[str, Dict[str, str]]:
        """Return a dictionary of translations."""
        return {
            "en": {
                # App title
                "app_title": "Source Code Exporter",
                # Main sections
                "history": "History",
                "export": "Export",
                # History view
                "export_history": "Export History",
                "configurations": "Saved Configurations",
                "new_export": "New Export",
                "no_configurations": "No saved configurations found. Create a new export configuration.",
                "confirm_delete_message": "Are you sure you want to delete this configuration?",
                "dark_theme": "Dark Theme",
                "light_theme": "Light Theme",
                # Common buttons
                "ok": "OK",
                "cancel": "Cancel",
                "back": "Back",
                "delete": "Delete",
                "browse": "Browse",
                "back_to_list": "Back to List",
                "delete_config": "Delete Config",
                "run_export": "Run Export",
                "settings": "Settings",
                # Export settings
                "export_configuration": "Export Configuration",
                "basic_settings": "Basic Settings",
                "advanced_settings": "Advanced Settings",
                "input_folder": "Input Folder",
                "output_file": "Output File",
                "output_format": "Output Format",
                "text_format": "Text",
                "markdown_format": "Markdown",
                "html_format": "HTML",
                "json_format": "JSON",
                "include_stats": "Include Statistics",
                "compare_previous": "Compare with Previous Export",
                "exclude_paths": "Exclude Paths",
                "exclude_extensions": "Exclude Extensions",
                "exclude_size_above": "Exclude Files Larger Than (KB)",
                "export_progress": "Export Progress",
                "preparing": "Preparing...",
                "analyzing": "Analyzing project structure...",
                "exporting": "Exporting files...",
                "export_complete": "Export complete!",
                "running": "Running...",
                "search": "Search",
                "sort_by": "Sort by:",
                "last_run": "Last Run",
                "project_path": "Project Path",
                "created": "Created",
                "run_count": "Run Count",
                "format": "Format",
                "delete_selected": "Delete Selected",
                "unknown": "Unknown",
                "never": "Never",
                # Common exclude patterns
                "common_exclude_patterns": "Common Exclude Patterns:",
                "exclude_node_modules": "• node_modules: JavaScript dependencies",
                "exclude_venv": "• venv, .venv: Python virtual environments",
                "exclude_build": "• build, dist: Build artifacts",
                "exclude_ide": "• .idea, .vscode: IDE settings",
                "exclude_git": "• .git: Git repository",
                # Tooltips
                "input_folder_tooltip": "Select the root directory of your project",
                "output_file_tooltip": "Specify where to save the exported content",
                "output_format_tooltip": "Select the format for the exported code",
                "text_format_tooltip": "Simple plain text format",
                "md_format_tooltip": "Markdown with code block syntax highlighting",
                "html_format_tooltip": "HTML with full syntax highlighting",
                "json_format_tooltip": "Structured JSON format for programmatic use",
                "include_stats_tooltip": "Include file counts and size statistics",
                "compare_previous_tooltip": "Show differences from the previous export",
                "exclude_paths_tooltip": "Specify paths to exclude from export",
                "exclude_paths_entry_tooltip": "Enter paths to exclude, separated by spaces",
                "exclude_extensions_tooltip": "Specify file extensions to exclude",
                "exclude_extensions_entry_tooltip": "Enter extensions to exclude, separated by spaces (e.g., .log .tmp .cache)",
                "exclude_size_tooltip": "Files larger than this size (in KB) will be excluded",
                "exclude_size_entry_tooltip": "Enter maximum file size in KB (0 means no limit)",
                "examples_tooltip": "Common patterns you might want to exclude",
                "browse_input_tooltip": "Browse to select input folder",
                "browse_output_tooltip": "Browse to select output file location",
                "browse_exclude_tooltip": "Browse to select paths to exclude",
                "help_tooltip": "Show help information",
                # New tooltips for file selection
                "select_folder_tooltip": "Click to browse for a folder",
                "select_file_tooltip": "Click to browse for a file",
                "select_exclude_folder": "Select Items to Exclude",
                "select_multiple_files_folders": "Would you like to select files or folders?",
                "select_files_button": "Select Files",
                "select_folders_button": "Select Folders",
                "select_both_button": "Select Both Files and Folders",
                "files_selected": "{} file(s) selected",
                "paths_excluded": "{} paths excluded",
                "path_outside_input": "Path is outside input folder: {0}",
                "error_relative_path": "Error creating relative path: {0}",
                # Error messages
                "error": "Error",
                "warning": "Warning",
                "info": "Information",
                "success": "Success",
                "input_folder_required": "Input folder is required.",
                "input_folder_not_exist": "Input folder does not exist.",
                "output_file_required": "Output file is required.",
                "export_failed": "Export Failed",
                "export_completed": "Export Completed",
                "open_output_file": "Open Output File",
                "no_items_selected": "No items selected.",
                "close": "Close",
                "confirm_delete": "Are you sure you want to delete {} selected item(s)?",
                # Exclude help
                "exclude_paths_help_title": "Exclude Paths Help",
                "exclude_paths_help": [
                    "Enter paths to exclude from the export, separated by spaces.",
                    "",
                    "Paths can be absolute or relative to the input folder.",
                    "",
                    "Examples:",
                    "node_modules - Excludes the node_modules directory",
                    "logs/*.log - Excludes .log files in the logs directory",
                    ".git - Excludes the .git directory",
                ],
                "exclude_extensions_help_title": "Exclude Extensions Help",
                "exclude_extensions_help": [
                    "Enter file extensions to exclude from the export, separated by spaces.",
                    "",
                    "Extensions should include the dot (.) prefix.",
                    "",
                    "Examples:",
                    ".jpg .png .gif - Excludes image files",
                    ".log .tmp - Excludes log and temporary files",
                    ".pyc .pyo - Excludes Python compiled files",
                ],
            },
            "vi": {
                # App title
                "app_title": "Trình Xuất Mã Nguồn",
                # Main sections
                "history": "Lịch Sử",
                "export": "Xuất",
                # History view
                "export_history": "Lịch Sử Xuất",
                "configurations": "Cấu Hình Đã Lưu",
                "new_export": "Xuất Mới",
                "no_configurations": "Không tìm thấy cấu hình đã lưu. Tạo một cấu hình xuất mới.",
                "confirm_delete_message": "Bạn có chắc chắn muốn xóa cấu hình này không?",
                "dark_theme": "Giao Diện Tối",
                "light_theme": "Giao Diện Sáng",
                # Common buttons
                "ok": "OK",
                "cancel": "Hủy",
                "back": "Quay Lại",
                "delete": "Xóa",
                "browse": "Duyệt",
                "back_to_list": "Quay Lại Danh Sách",
                "delete_config": "Xóa Cấu Hình",
                "run_export": "Chạy Xuất",
                "settings": "Cài Đặt",
                # Export settings
                "export_configuration": "Cấu Hình Xuất",
                "basic_settings": "Cài Đặt Cơ Bản",
                "advanced_settings": "Cài Đặt Nâng Cao",
                "input_folder": "Thư Mục Đầu Vào",
                "output_file": "Tệp Đầu Ra",
                "output_format": "Định Dạng Đầu Ra",
                "text_format": "Văn Bản",
                "markdown_format": "Markdown",
                "html_format": "HTML",
                "json_format": "JSON",
                "include_stats": "Bao Gồm Thống Kê",
                "compare_previous": "So Sánh Với Lần Xuất Trước",
                "exclude_paths": "Loại Trừ Đường Dẫn",
                "exclude_extensions": "Loại Trừ Phần Mở Rộng",
                "exclude_size_above": "Loại Trừ Tệp Lớn Hơn (KB)",
                "export_progress": "Tiến Trình Xuất",
                "preparing": "Đang chuẩn bị...",
                "analyzing": "Đang phân tích cấu trúc dự án...",
                "exporting": "Đang xuất tệp...",
                "export_complete": "Xuất hoàn thành!",
                "running": "Đang chạy...",
                "search": "Tìm Kiếm",
                "sort_by": "Sắp xếp theo:",
                "last_run": "Lần Chạy Cuối",
                "project_path": "Đường Dẫn Dự Án",
                "created": "Đã Tạo",
                "run_count": "Số Lần Chạy",
                "format": "Định Dạng",
                "delete_selected": "Xóa Đã Chọn",
                "unknown": "Không Xác Định",
                "never": "Chưa Bao Giờ",
                # Common exclude patterns
                "common_exclude_patterns": "Mẫu Loại Trừ Phổ Biến:",
                "exclude_node_modules": "• node_modules: Thư viện JavaScript",
                "exclude_venv": "• venv, .venv: Môi trường ảo Python",
                "exclude_build": "• build, dist: Thành phần xây dựng",
                "exclude_ide": "• .idea, .vscode: Cài đặt IDE",
                "exclude_git": "• .git: Kho lưu trữ Git",
                # Tooltips
                "input_folder_tooltip": "Chọn thư mục gốc của dự án của bạn",
                "output_file_tooltip": "Chỉ định nơi lưu nội dung xuất",
                "output_format_tooltip": "Chọn định dạng cho mã được xuất",
                "text_format_tooltip": "Định dạng văn bản đơn giản",
                "md_format_tooltip": "Markdown với bôi đậm cú pháp khối mã",
                "html_format_tooltip": "HTML với bôi đậm cú pháp đầy đủ",
                "json_format_tooltip": "Định dạng JSON có cấu trúc để sử dụng lập trình",
                "include_stats_tooltip": "Bao gồm số lượng tệp và thống kê kích thước",
                "compare_previous_tooltip": "Hiển thị sự khác biệt từ lần xuất trước",
                "exclude_paths_tooltip": "Chỉ định đường dẫn để loại trừ khỏi xuất",
                "exclude_paths_entry_tooltip": "Nhập đường dẫn để loại trừ, ngăn cách bằng dấu cách",
                "exclude_extensions_tooltip": "Chỉ định phần mở rộng tệp để loại trừ",
                "exclude_extensions_entry_tooltip": "Nhập phần mở rộng để loại trừ, ngăn cách bằng dấu cách (ví dụ: .log .tmp .cache)",
                "exclude_size_tooltip": "Các tệp lớn hơn kích thước này (tính bằng KB) sẽ bị loại trừ",
                "exclude_size_entry_tooltip": "Nhập kích thước tệp tối đa bằng KB (0 có nghĩa là không giới hạn)",
                "examples_tooltip": "Các mẫu phổ biến bạn có thể muốn loại trừ",
                "browse_input_tooltip": "Duyệt để chọn thư mục đầu vào",
                "browse_output_tooltip": "Duyệt để chọn vị trí tệp đầu ra",
                "browse_exclude_tooltip": "Duyệt để chọn đường dẫn loại trừ",
                "help_tooltip": "Hiển thị thông tin trợ giúp",
                # New tooltips for file selection
                "select_folder_tooltip": "Nhấn để chọn thư mục",
                "select_file_tooltip": "Nhấn để chọn tệp",
                "select_exclude_folder": "Chọn mục để loại trừ",
                "select_multiple_files_folders": "Bạn muốn chọn tệp hay thư mục?",
                "select_files_button": "Chọn tệp",
                "select_folders_button": "Chọn thư mục",
                "select_both_button": "Chọn cả tệp và thư mục",
                "files_selected": "{} tệp đã được chọn",
                "paths_excluded": "{} đường dẫn đã được loại trừ",
                "path_outside_input": "Đường dẫn nằm ngoài thư mục đầu vào: {0}",
                "error_relative_path": "Lỗi tạo đường dẫn tương đối: {0}",
                # Error messages
                "error": "Lỗi",
                "warning": "Cảnh Báo",
                "info": "Thông Tin",
                "success": "Thành Công",
                "input_folder_required": "Thư mục đầu vào là bắt buộc.",
                "input_folder_not_exist": "Thư mục đầu vào không tồn tại.",
                "output_file_required": "Tệp đầu ra là bắt buộc.",
                "export_failed": "Xuất Thất Bại",
                "export_completed": "Xuất Hoàn Thành",
                "open_output_file": "Mở Tệp Đầu Ra",
                "no_items_selected": "Không có mục nào được chọn.",
                "close": "Đóng",
                "confirm_delete": "Bạn có chắc chắn muốn xóa {} mục đã chọn không?",
                # Exclude help
                "exclude_paths_help_title": "Trợ Giúp Loại Trừ Đường Dẫn",
                "exclude_paths_help": [
                    "Nhập đường dẫn để loại trừ khỏi xuất, ngăn cách bằng dấu cách.",
                    "",
                    "Đường dẫn có thể là tuyệt đối hoặc tương đối với thư mục đầu vào.",
                    "",
                    "Ví dụ:",
                    "node_modules - Loại trừ thư mục node_modules",
                    "logs/*.log - Loại trừ tệp .log trong thư mục logs",
                    ".git - Loại trừ thư mục .git",
                ],
                "exclude_extensions_help_title": "Trợ Giúp Loại Trừ Phần Mở Rộng",
                "exclude_extensions_help": [
                    "Nhập phần mở rộng tệp để loại trừ khỏi xuất, ngăn cách bằng dấu cách.",
                    "",
                    "Phần mở rộng nên bao gồm tiền tố dấu chấm (.).",
                    "",
                    "Ví dụ:",
                    ".jpg .png .gif - Loại trừ tệp hình ảnh",
                    ".log .tmp - Loại trừ tệp nhật ký và tệp tạm thời",
                    ".pyc .pyo - Loại trừ tệp biên dịch Python",
                ],
            },
        }

    def get_text(self, key: str, default: Optional[str] = None, *args) -> str:
        """Get translated text for a key."""
        # Get the correct language translations
        current_translations = self.translations.get(self.current_language, {})
        text = current_translations.get(key, default or key)

        # Debug logging for important keys
        if key in ["new_export", "export_history", "settings", "delete_selected"]:
            logging.debug(
                f"get_text('{key}') -> '{text}' (lang: {self.current_language})"
            )

        # Format with args if provided
        if args:
            try:
                return text.format(*args)
            except Exception as e:
                logging.error(f"Error formatting text '{key}': {e}")
                return text

        return text

    def change_language(self, language: str) -> None:
        """Change the current language."""
        if language not in self.AVAILABLE_LANGUAGES:
            logging.warning(f"Unknown language: {language}. Using default.")
            return

        self.current_language = language
        self.load_translations()
        self.save_settings()

    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language

    def get_language_name(self, language_code: Optional[str] = None) -> str:
        """Get the name of a language by its code."""
        code = language_code or self.current_language
        return self.AVAILABLE_LANGUAGES.get(code, code)

    def debug_translations(self) -> None:
        """Debug method to print current translations."""
        logging.debug(f"Current language: {self.current_language}")
        logging.debug(f"Available languages: {list(self.translations.keys())}")
        current_translations = self.translations.get(self.current_language, {})
        logging.debug(
            f"Current translations keys: {list(current_translations.keys())[:10]}"
        )
        logging.debug(
            f"'new_export' translation: {current_translations.get('new_export', 'NOT FOUND')}"
        )
        logging.debug(
            f"'export_history' translation: {current_translations.get('export_history', 'NOT FOUND')}"
        )
