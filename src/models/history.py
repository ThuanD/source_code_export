import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class ExportHistory:
    """Manages the history of export operations."""

    def __init__(self, history_file_path: Path):
        """Initialize with path to the history file."""
        self.history_file_path = history_file_path
        self.history_data = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Load history data from file."""
        if not self.history_file_path.exists():
            logging.info(
                f"History file {self.history_file_path} does not exist. Creating a new one."
            )
            self.history_data = {}
            return self.history_data

        try:
            with self.history_file_path.open("r", encoding="utf-8") as f:
                self.history_data = json.load(f)
                logging.info(f"Loaded {len(self.history_data)} history entries.")
                return self.history_data
        except json.JSONDecodeError:
            logging.warning(
                f"Invalid JSON in history file {self.history_file_path}. Creating a new one."
            )
            self.history_data = {}
        except Exception as e:
            logging.error(f"Error loading history file: {e}")
            self.history_data = {}

        return self.history_data

    def save(self) -> bool:
        """Save history data to file."""
        try:
            # Make sure parent directory exists
            self.history_file_path.parent.mkdir(parents=True, exist_ok=True)

            with self.history_file_path.open("w", encoding="utf-8") as f:
                json.dump(self.history_data, f, indent=2)
                logging.info(f"Saved {len(self.history_data)} history entries.")
                return True
        except Exception as e:
            logging.error(f"Error saving history file: {e}")
            return False

    def add_entry(self, path: str, params: Dict[str, Any]) -> None:
        """Add or update an entry in the history."""
        # Update entry with current timestamp
        params["last_run"] = datetime.now().timestamp()
        params["last_run_formatted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # If this is a new entry, add created timestamp
        if path not in self.history_data:
            params["created"] = datetime.now().timestamp()
            params["created_formatted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Keep track of the number of runs
        if "run_count" in self.history_data.get(path, {}):
            params["run_count"] = self.history_data[path]["run_count"] + 1
        else:
            params["run_count"] = 1

        # Store previous output format and size stats if available
        if path in self.history_data and "output_file" in self.history_data[path]:
            params["previous_output"] = self.history_data[path]["output_file"]

        if path in self.history_data and "stats" in self.history_data[path]:
            params["previous_stats"] = self.history_data[path]["stats"]

        # Update the entry
        self.history_data[path] = params
        self.save()

    def update_stats(self, path: str, stats: Dict[str, Any]) -> None:
        """Update the stats for a specific history entry."""
        if path in self.history_data:
            self.history_data[path]["stats"] = stats
            self.save()

    def get_entry(self, path: str) -> Optional[Dict[str, Any]]:
        """Get a specific history entry."""
        return self.history_data.get(path)

    def get_all_entries(self) -> Dict[str, Any]:
        """Get all history entries."""
        return self.history_data

    def get_sorted_entries(
        self, sort_by: str = "last_run", reverse: bool = True
    ) -> List[Dict[str, Any]]:
        """Get history entries sorted by the specified key."""
        entries = []

        for path, entry in self.history_data.items():
            # Add path to the entry for convenience
            entry_with_path = entry.copy()
            entry_with_path["path"] = path
            entries.append(entry_with_path)

        if sort_by == "path":
            return sorted(entries, key=lambda x: x["path"].lower(), reverse=reverse)
        elif sort_by == "created":
            return sorted(entries, key=lambda x: x.get("created", 0), reverse=reverse)
        elif sort_by == "run_count":
            return sorted(entries, key=lambda x: x.get("run_count", 0), reverse=reverse)
        else:  # Default to last_run
            return sorted(entries, key=lambda x: x.get("last_run", 0), reverse=reverse)

    def delete_entry(self, path: str) -> bool:
        """Delete a specific history entry."""
        if path in self.history_data:
            del self.history_data[path]
            return self.save()
        return False

    def delete_entries(self, paths: List[str]) -> int:
        """Delete multiple history entries."""
        deleted_count = 0

        for path in paths:
            if path in self.history_data:
                del self.history_data[path]
                deleted_count += 1

        if deleted_count > 0:
            self.save()

        return deleted_count

    def clear_all(self) -> bool:
        """Clear all history entries."""
        self.history_data = {}
        return self.save()

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """Search for entries containing the query string."""
        query = query.lower()
        results = []

        for path, entry in self.history_data.items():
            # Search in path
            if query in path.lower():
                entry_with_path = entry.copy()
                entry_with_path["path"] = path
                results.append(entry_with_path)
                continue

            # Search in output file name
            output_file = entry.get("output_file", "")
            if output_file and query in output_file.lower():
                entry_with_path = entry.copy()
                entry_with_path["path"] = path
                results.append(entry_with_path)
                continue

            # Search in exclude patterns
            exclude_paths = entry.get("exclude_paths", [])
            if any(query in exclude.lower() for exclude in exclude_paths):
                entry_with_path = entry.copy()
                entry_with_path["path"] = path
                results.append(entry_with_path)
                continue

        return results
