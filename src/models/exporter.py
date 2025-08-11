import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, TextIO, Tuple


class SourceCodeExporter:
    """Enhanced Source Code Exporter with advanced features."""

    def __init__(
        self,
        root_path: str,
        exclude_paths: List[str] = None,
        exclude_extensions: List[str] = None,
        exclude_size_above: int = 0,  # Size in KB
        output_format: str = "txt",
    ) -> None:
        """Initialize exporter with root path and exclude patterns."""
        self.root_path = Path(root_path)
        self.exclude_paths = set(exclude_paths or [])
        self.exclude_extensions = set(exclude_extensions or [])
        self.exclude_size_above = exclude_size_above * 1024  # Convert to bytes
        self.output_format = output_format.lower()
        self.default_excludes = {
            ".idea",
            ".ruff_cache",
            ".git",
            ".pytest_cache",
            "__pycache__",
            ".env",
            ".venv",
            "venv",
            "node_modules",
            ".DS_Store",
            "source_code_export.txt",
        }

        # Statistics tracking
        self.stats = {
            "total_files": 0,
            "total_dirs": 0,
            "total_size": 0,
            "file_types": {},
            "exported_files": 0,
            "exported_size": 0,
            "skipped_files": 0,
        }

        # Progress tracking
        self.total_items = 0
        self.processed_items = 0
        self.current_file = ""

        # Output specific options
        self.max_file_preview_size = 1024 * 100  # 100KB

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        # Check default excludes
        if any(parent.name in self.default_excludes for parent in path.parents):
            return True
        if path.name in self.default_excludes:
            return True

        # Check exclude patterns
        if any(path.match(exclude) for exclude in self.exclude_paths):
            return True

        # Check file extensions
        if path.is_file() and path.suffix.lower() in self.exclude_extensions:
            return True

        # Check file size
        if self.exclude_size_above > 0 and path.is_file():
            try:
                if path.stat().st_size > self.exclude_size_above:
                    return True
            except Exception:
                # If we can't stat the file, better be safe and include it
                pass

        return False

    def count_items(self) -> int:
        """Count total items to process for progress tracking."""
        count = 0
        stack = [self.root_path]

        while stack:
            current = stack.pop()

            if self._should_exclude(current):
                continue

            try:
                if current.is_dir():
                    self.stats["total_dirs"] += 1
                    for child in current.iterdir():
                        stack.append(child)
                else:
                    count += 1
                    self.stats["total_files"] += 1
                    # Update file type stats
                    ext = current.suffix.lower() or "no_extension"
                    self.stats["file_types"][ext] = (
                        self.stats["file_types"].get(ext, 0) + 1
                    )
                    # Update total size
                    try:
                        file_size = current.stat().st_size
                        self.stats["total_size"] += file_size
                    except Exception:
                        pass
            except Exception as e:
                logging.warning(f"Error accessing {current}: {e}")

        self.total_items = count
        return count

    def export_structure(self, output_file: Path) -> Dict[str, Any]:
        """Export directory structure and file contents to the specified output format."""
        # Initialize progress tracking
        self.count_items()
        self.processed_items = 0

        # Select the right output format handler
        if self.output_format == "html":
            return self._export_html(output_file)
        elif self.output_format == "md" or self.output_format == "markdown":
            return self._export_markdown(output_file)
        elif self.output_format == "json":
            return self._export_json(output_file)
        else:  # Default to text format
            return self._export_text(output_file)

    def _export_text(self, output_file: Path) -> Dict[str, Any]:
        """Export to plain text format."""
        with Path(output_file).open("w", encoding="utf-8") as f:
            # Write header
            f.write(f"Project Structure: {self.root_path.name}\n")
            f.write("=" * 50 + "\n\n")

            # Write stats summary
            f.write("Project Statistics:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Directories: {self.stats['total_dirs']}\n")
            f.write(f"Total Files: {self.stats['total_files']}\n")
            f.write(f"Total Size: {self._format_size(self.stats['total_size'])}\n\n")

            # Write directory structure
            f.write("Directory Structure:\n")
            f.write("-" * 20 + "\n")
            self._write_structure(self.root_path, f)
            f.write("\n\n")

            # Write file contents
            f.write("File Contents:\n")
            f.write("-" * 20 + "\n")
            self._write_contents(self.root_path, f)

        # Return the stats
        return self.stats

    def _export_markdown(self, output_file: Path) -> Dict[str, Any]:
        """Export to Markdown format."""
        with Path(output_file).open("w", encoding="utf-8") as f:
            # Write header
            f.write(f"# Project Structure: {self.root_path.name}\n\n")

            # Write stats summary
            f.write("## Project Statistics\n\n")
            f.write(f"- **Total Directories:** {self.stats['total_dirs']}\n")
            f.write(f"- **Total Files:** {self.stats['total_files']}\n")
            f.write(
                f"- **Total Size:** {self._format_size(self.stats['total_size'])}\n\n"
            )

            # Write directory structure
            f.write("## Directory Structure\n\n")
            f.write("```\n")
            self._write_structure(self.root_path, f)
            f.write("```\n\n")

            # Write file contents
            f.write("## File Contents\n\n")
            self._write_contents_markdown(self.root_path, f)

        # Return the stats
        return self.stats

    def _export_html(self, output_file: Path) -> Dict[str, Any]:
        """Export to HTML format with syntax highlighting."""
        with Path(output_file).open("w", encoding="utf-8") as f:
            # Write HTML header
            f.write(
                """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Source Code Export</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }
        .dark-mode { background-color: #1e1e1e; color: #ddd; }
        h1, h2, h3 { color: #0066cc; }
        .dark-mode h1, .dark-mode h2, .dark-mode h3 { color: #58a6ff; }
        .stats { display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px; }
        .stat-card { border: 1px solid #ddd; border-radius: 4px; padding: 10px; flex: 1; min-width: 200px; }
        .dark-mode .stat-card { border-color: #444; background-color: #252525; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow: auto; }
        .dark-mode pre { background-color: #2d2d2d; }
        .file-header { background-color: #e0e0e0; padding: 8px; margin-top: 20px; border-radius: 4px 4px 0 0; }
        .dark-mode .file-header { background-color: #383838; }
        .theme-toggle { position: fixed; top: 20px; right: 20px; padding: 8px 16px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .dark-mode .theme-toggle { background: #1a4971; }
    </style>
    <script>
        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('dark-mode', document.body.classList.contains('dark-mode'));
        }
        
        window.onload = function() {
            if (localStorage.getItem('dark-mode') === 'true') {
                document.body.classList.add('dark-mode');
            }
        }
    </script>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
    <h1>Project Structure: %s</h1>
    
    <h2>Project Statistics</h2>
    <div class="stats">
        <div class="stat-card">
            <h3>Files & Directories</h3>
            <p>Total Directories: %d</p>
            <p>Total Files: %d</p>
            <p>Total Size: %s</p>
        </div>
        <div class="stat-card">
            <h3>File Types</h3>
            <ul>
"""
                % (
                    self.root_path.name,
                    self.stats["total_dirs"],
                    self.stats["total_files"],
                    self._format_size(self.stats["total_size"]),
                )
            )

            # Write file type stats
            for ext, count in sorted(
                self.stats["file_types"].items(), key=lambda x: x[1], reverse=True
            )[:10]:
                f.write(f"                <li>{ext}: {count}</li>\n")

            f.write("""            </ul>
        </div>
    </div>
    
    <h2>Directory Structure</h2>
    <pre>
""")

            # Write directory structure
            self._write_structure_html(self.root_path, f)

            f.write("""    </pre>
    
    <h2>File Contents</h2>
""")

            # Write file contents with syntax highlighting
            self._write_contents_html(self.root_path, f)

            # Write HTML footer
            f.write(
                """
    <footer style="margin-top: 50px; text-align: center; color: #777;">
        <p>Generated on %s</p>
    </footer>
</body>
</html>
"""
                % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        # Return the stats
        return self.stats

    def _export_json(self, output_file: Path) -> Dict[str, Any]:
        """Export to JSON format."""
        structure = {
            "project_name": self.root_path.name,
            "stats": self.stats,
            "structure": self._build_json_structure(self.root_path),
            "generated_at": datetime.now().isoformat(),
        }

        with Path(output_file).open("w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2)

        return self.stats

    def _build_json_structure(self, path: Path, rel_path: str = "") -> Dict[str, Any]:
        """Build a JSON representation of the directory structure."""
        if self._should_exclude(path):
            return None

        if not rel_path:
            rel_path = path.name

        result = {
            "name": path.name,
            "path": str(rel_path),
            "type": "directory" if path.is_dir() else "file",
        }

        if path.is_dir():
            result["children"] = []
            try:
                for child in sorted(
                    path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
                ):
                    child_rel_path = (
                        f"{rel_path}/{child.name}" if rel_path else child.name
                    )
                    child_data = self._build_json_structure(child, child_rel_path)
                    if child_data:
                        result["children"].append(child_data)
            except Exception as e:
                logging.warning(f"Error accessing directory {path}: {e}")
        else:
            # For files, include metadata
            try:
                stats = path.stat()
                result["size"] = stats.st_size
                result["modified"] = datetime.fromtimestamp(stats.st_mtime).isoformat()

                # Include content for text files that aren't too big
                if (
                    self._is_text_file(path)
                    and stats.st_size <= self.max_file_preview_size
                ):
                    try:
                        with path.open("r", encoding="utf-8") as f:
                            result["content"] = f.read()
                    except Exception as e:
                        result["error"] = f"Could not read file: {str(e)}"

            except Exception as e:
                result["error"] = f"Could not stat file: {str(e)}"

        return result

    def _get_indent(self, level: int) -> str:
        """Create indentation for directory structure."""
        if level == 0:
            return ""
        return "  " * (level - 1) + "├── "

    def _write_structure(self, current_path: Path, f: TextIO, level: int = 0) -> None:
        """Recursively write directory structure in text format."""
        if self._should_exclude(current_path):
            return

        if level > 0:  # Don't write root directory
            f.write(f"{self._get_indent(level)}{current_path.name}\n")

        if current_path.is_dir():
            # Update progress
            self.current_file = str(current_path.relative_to(self.root_path))

            # Sort files and directories
            paths = []
            try:
                paths = sorted(
                    current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
                )
            except Exception as e:
                logging.warning(f"Error accessing directory {current_path}: {e}")

            for path in paths:
                self._write_structure(path, f, level + 1)

    def _write_structure_html(
        self, current_path: Path, f: TextIO, level: int = 0
    ) -> None:
        """Recursively write directory structure in HTML format."""
        if self._should_exclude(current_path):
            return

        indent = "    " * level
        if level > 0:  # Don't write root directory
            icon = "📁" if current_path.is_dir() else "📄"
            f.write(f"{indent}{icon} {current_path.name}\n")

        if current_path.is_dir():
            # Update progress
            self.current_file = str(current_path.relative_to(self.root_path))

            # Sort files and directories
            paths = []
            try:
                paths = sorted(
                    current_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
                )
            except Exception as e:
                logging.warning(f"Error accessing directory {current_path}: {e}")

            for path in paths:
                self._write_structure_html(path, f, level + 1)

    def _write_contents(self, current_path: Path, f: TextIO) -> None:
        """Recursively write file contents in text format."""
        if self._should_exclude(current_path):
            self.stats["skipped_files"] += 1
            return

        if current_path.is_file():
            # Update progress
            self.processed_items += 1
            self.current_file = str(current_path.relative_to(self.root_path))

            # Only write contents of text files
            if self._is_text_file(current_path):
                try:
                    file_size = current_path.stat().st_size
                    self.stats["exported_files"] += 1
                    self.stats["exported_size"] += file_size

                    f.write(f"\nFile: {current_path.relative_to(self.root_path)}\n")
                    f.write("-" * 50 + "\n")

                    # For large files, only show a preview
                    if file_size > self.max_file_preview_size:
                        with current_path.open("r", encoding="utf-8") as source_file:
                            f.write(source_file.read(self.max_file_preview_size))
                            f.write("\n\n... (file truncated due to size) ...\n")
                    else:
                        with current_path.open("r", encoding="utf-8") as source_file:
                            f.write(source_file.read())
                    f.write("\n")
                except Exception as e:
                    f.write(f"Error reading file: {str(e)}\n")
        else:
            for path in sorted(current_path.iterdir()):
                self._write_contents(path, f)

    def _write_contents_markdown(self, current_path: Path, f: TextIO) -> None:
        """Recursively write file contents in Markdown format."""
        if self._should_exclude(current_path):
            return

        if current_path.is_file():
            # Update progress
            self.processed_items += 1
            self.current_file = str(current_path.relative_to(self.root_path))

            # Only write contents of text files
            if self._is_text_file(current_path):
                try:
                    file_size = current_path.stat().st_size
                    rel_path = current_path.relative_to(self.root_path)

                    f.write(f"\n### File: {rel_path}\n\n")

                    # Determine language for syntax highlighting
                    lang = self._get_markdown_language(current_path.suffix)

                    # For large files, only show a preview
                    if file_size > self.max_file_preview_size:
                        with current_path.open("r", encoding="utf-8") as source_file:
                            f.write(f"```{lang}\n")
                            f.write(source_file.read(self.max_file_preview_size))
                            f.write("\n```\n\n")
                            f.write("*... (file truncated due to size) ...*\n")
                    else:
                        with current_path.open("r", encoding="utf-8") as source_file:
                            f.write(f"```{lang}\n")
                            f.write(source_file.read())
                            f.write("\n```\n")
                except Exception as e:
                    f.write(f"*Error reading file: {str(e)}*\n")
        else:
            for path in sorted(current_path.iterdir()):
                self._write_contents_markdown(path, f)

    def _write_contents_html(self, current_path: Path, f: TextIO) -> None:
        """Recursively write file contents in HTML format."""
        if self._should_exclude(current_path):
            return

        if current_path.is_file():
            # Update progress
            self.processed_items += 1
            self.current_file = str(current_path.relative_to(self.root_path))

            # Only write contents of text files
            if self._is_text_file(current_path):
                try:
                    file_size = current_path.stat().st_size
                    rel_path = current_path.relative_to(self.root_path)

                    f.write(f'<div class="file-header">{rel_path}</div>\n<pre>\n')

                    # For large files, only show a preview
                    if file_size > self.max_file_preview_size:
                        with current_path.open("r", encoding="utf-8") as source_file:
                            content = source_file.read(self.max_file_preview_size)
                            # Escape HTML characters
                            content = (
                                content.replace("&", "&amp;")
                                .replace("<", "&lt;")
                                .replace(">", "&gt;")
                            )
                            f.write(content)
                            f.write("\n\n... (file truncated due to size) ...")
                    else:
                        with current_path.open("r", encoding="utf-8") as source_file:
                            content = source_file.read()
                            # Escape HTML characters
                            content = (
                                content.replace("&", "&amp;")
                                .replace("<", "&lt;")
                                .replace(">", "&gt;")
                            )
                            f.write(content)
                    f.write("\n</pre>\n")
                except Exception as e:
                    f.write(f"<p>Error reading file: {str(e)}</p>\n")
        else:
            for path in sorted(current_path.iterdir()):
                self._write_contents_html(path, f)

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file based on extension and content."""
        # Common text file extensions
        text_extensions = {
            # Code files
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".html",
            ".css",
            ".scss",
            ".sass",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".swift",
            ".kt",
            ".kts",
            ".dart",
            ".scala",
            ".groovy",
            ".lua",
            ".pl",
            ".r",
            # Config and data files
            ".json",
            ".yml",
            ".yaml",
            ".xml",
            ".ini",
            ".conf",
            ".config",
            ".properties",
            ".toml",
            ".env",
            ".sql",
            ".graphql",
            ".prisma",
            ".proto",
            # Documentation files
            ".md",
            ".rst",
            ".txt",
            ".tex",
            ".csv",
            ".adoc",
            ".wiki",
            # Shell scripts
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
            ".bat",
            ".cmd",
            ".ps1",
            # Web specific
            ".vue",
            ".svelte",
            ".astro",
            ".pug",
            ".jade",
            ".ejs",
            ".hbs",
            ".handlebars",
            # Other text formats
            ".log",
            ".diff",
            ".patch",
            ".gitignore",
        }

        # Quick check by extension first (most efficient)
        extension = file_path.suffix.lower()
        if extension in text_extensions:
            return True

        # For unknown extensions, try to peek at the content
        # This avoids loading large binary files into memory
        try:
            # Check file size first
            if file_path.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                return False

            # Try to read first few KB as text
            with open(file_path, "rb") as f:
                content = f.read(4096)  # Read first 4KB

                # Check for common binary file signatures
                if content.startswith(b"PK\x03\x04"):  # ZIP files
                    return False
                if b"\x00" in content[:1000]:  # Null bytes in first 1000 bytes
                    return False

                # Try to decode as UTF-8
                try:
                    content.decode("utf-8")
                    return True
                except UnicodeDecodeError:
                    # Try other common encodings
                    try:
                        content.decode("latin-1")
                        return True
                    except Exception:
                        return False
        except Exception:
            # If any error occurs, be conservative and skip the file
            return False

        return False

    def _get_markdown_language(self, extension: str) -> str:
        """Get Markdown code block language based on file extension."""
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".md": "markdown",
            ".sh": "bash",
            ".bash": "bash",
            ".sql": "sql",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".swift": "swift",
            ".kt": "kotlin",
            ".kts": "kotlin",
        }
        return lang_map.get(extension.lower(), "")

    def _format_size(self, size_bytes: int) -> str:
        """Format a byte size into a human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024 or unit == "GB":
                if unit == "B":
                    return f"{size_bytes} {unit}"
                return f"{size_bytes / 1024:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"  # Should never reach here for code projects

    def get_progress(self) -> Tuple[int, int, str]:
        """Return the current progress as (current, total, current_file)."""
        return self.processed_items, self.total_items, self.current_file

    def compare_exports(self, previous_export_path: Path) -> Dict[str, Any]:
        """Compare current export with a previous one."""
        try:
            with previous_export_path.open("r", encoding="utf-8") as f:
                if previous_export_path.suffix.lower() == ".json":
                    # If previous export is JSON, we can do a more detailed comparison
                    prev_data = json.load(f)
                    return self._compare_json_exports(prev_data)
                else:
                    # For text exports, we can do a basic file count comparison
                    return self._compare_text_exports(f.read())
        except Exception as e:
            return {"error": f"Could not compare exports: {str(e)}"}

    def _compare_json_exports(self, prev_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare with previous JSON export."""
        current_stats = self.stats.copy()
        prev_stats = prev_data.get("stats", {})

        # Calculate differences
        diff = {
            "files_diff": current_stats.get("total_files", 0)
            - prev_stats.get("total_files", 0),
            "dirs_diff": current_stats.get("total_dirs", 0)
            - prev_stats.get("total_dirs", 0),
            "size_diff": current_stats.get("total_size", 0)
            - prev_stats.get("total_size", 0),
            "file_types_diff": {},
        }

        # Compare file types
        current_types = current_stats.get("file_types", {})
        prev_types = prev_stats.get("file_types", {})

        all_types = set(current_types.keys()) | set(prev_types.keys())
        for ext in all_types:
            current_count = current_types.get(ext, 0)
            prev_count = prev_types.get(ext, 0)
            if current_count != prev_count:
                diff["file_types_diff"][ext] = current_count - prev_count

        return {"current": current_stats, "previous": prev_stats, "diff": diff}

    def _compare_text_exports(self, prev_content: str) -> Dict[str, Any]:
        """Perform a basic comparison with previous text export."""
        # Very basic comparison - just count lines and file references
        prev_files = prev_content.count("\nFile: ")

        return {
            "current": {
                "total_files": self.stats["total_files"],
                "total_dirs": self.stats["total_dirs"],
            },
            "diff": {
                "lines_diff": "Unknown",
                "files_diff": self.stats["total_files"] - prev_files,
            },
        }
