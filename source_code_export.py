import argparse
import logging
from pathlib import Path
from typing import List, TextIO

logging.basicConfig(level=logging.INFO, format="%(message)s")


class SourceCodeExporter:
    """Export source code structure and contents to text file."""

    def __init__(
        self,
        root_path: str,
        exclude_paths: List[str] = None,
        exclude_extensions: List[str] = None,
    ) -> None:
        """Initialize exporter with root path and exclude patterns."""
        self.root_path = Path(root_path)
        self.exclude_paths = set(exclude_paths or [])
        self.exclude_extensions = set(exclude_extensions or [])
        self.default_excludes = {
            ".idea",
            ".ruff_cache",
            ".git",
            ".pytest_cache",
            "__pycache__",
            ".env",
            ".venv",
            "venv",
            "source_code_export.py",
            "source_code_export.txt",
        }

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        if any(parent.name in self.default_excludes for parent in path.parents):
            return True
        if path.name in self.default_excludes:
            return True
        if any(path.match(exclude) for exclude in self.exclude_paths):
            return True
        if path.is_file() and path.suffix in self.exclude_extensions:
            return True
        return False

    def _get_indent(self, level: int) -> str:
        """Create indentation for directory structure."""
        return "  " * level + "├── "

    def export_structure(self, output_file: Path) -> None:
        """Export directory structure and file contents to text file."""
        with Path(output_file).open("w", encoding="utf-8") as f:
            # Write header
            f.write(f"Project Structure: {self.root_path.name}\n")
            f.write("=" * 50 + "\n\n")

            # Write directory structure
            f.write("Directory Structure:\n")
            f.write("-" * 20 + "\n")
            self._write_structure(self.root_path, f)
            f.write("\n\n")

            # Write file contents
            f.write("File Contents:\n")
            f.write("-" * 20 + "\n")
            self._write_contents(self.root_path, f)

    def _write_structure(self, current_path: Path, f: TextIO, level: int = 0) -> None:
        """Recursively write directory structure."""
        if self._should_exclude(current_path):
            return

        if level > 0:  # Don't write root directory
            f.write(f"{self._get_indent(level - 1)}{current_path.name}\n")

        if current_path.is_dir():
            # Sort files and directories
            paths = sorted(
                current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
            )

            for path in paths:
                self._write_structure(path, f, level + 1)

    def _write_contents(self, current_path: Path, f: TextIO) -> None:
        """Recursively write file contents."""
        if self._should_exclude(current_path):
            return

        if current_path.is_file():
            # Only write contents of text files
            if self._is_text_file(current_path):
                f.write(f"\nFile: {current_path.relative_to(self.root_path)}\n")
                f.write("-" * 50 + "\n")
                try:
                    with Path.open(current_path, encoding="utf-8") as source_file:
                        f.write(source_file.read())
                    f.write("\n")
                except Exception as e:
                    f.write(f"Error reading file: {str(e)}\n")
        else:
            for path in sorted(current_path.iterdir()):
                self._write_contents(path, f)

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file based on extension."""
        text_extensions = {
            ".txt",
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".html",
            ".css",
            ".json",
            ".yml",
            ".yaml",
            ".md",
            ".rst",
            ".ini",
            ".conf",
            ".sh",
            ".bash",
            ".env",
            ".sql",
            ".xml",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".rb",
            ".go",
        }
        return file_path.suffix.lower() in text_extensions


def main() -> None:
    """Parse command-line arguments and export source code."""
    parser = argparse.ArgumentParser(
        description="Export source code structure and contents to text file"
    )
    parser.add_argument("path", help="Root path of the project")
    parser.add_argument(
        "--output",
        "-o",
        default="source_code_export.txt",
        help="Output file path (default: source_code_export.txt)",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        nargs="*",
        default=[],
        help="Paths to exclude (supports glob patterns)",
    )
    parser.add_argument(
        "--exclude-ext",
        nargs="*",
        default=[],
        help="File extensions to exclude (e.g., .pyc .jar)",
    )

    args = parser.parse_args()

    exporter = SourceCodeExporter(
        args.path, exclude_paths=args.exclude, exclude_extensions=args.exclude_ext
    )

    exporter.export_structure(args.output)
    logging.info(f"\033[92mExport completed: Output written to: {args.output}.\033[0m")


if __name__ == "__main__":
    main()
