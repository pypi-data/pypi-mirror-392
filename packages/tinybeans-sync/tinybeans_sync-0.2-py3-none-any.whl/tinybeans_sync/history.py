#!/usr/bin/env python3
"""
Download history tracking for Tinybeans
"""
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DownloadHistory:
    def __init__(self, history_file='.tinybeans_history.json'):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self):
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                logger.warning("Could not load %s, starting fresh", self.history_file)
                return {}
        return {}

    def _save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            logger.warning("Could not save history %s: %s", self.history_file, e)

    def is_attempted(self, filename):
        """Check if filename has been attempted before"""
        return filename in self.history

    def mark_attempted(self, filename, timestamp=None):
        """Mark filename as attempted with timestamp"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        self.history[filename] = timestamp
        self._save_history()

    def get_latest_timestamp(self):
        """Get the most recent timestamp from history"""
        if not self.history:
            return None

        timestamps = [datetime.fromisoformat(ts.replace('Z', '+00:00'))
                     for ts in self.history.values()]
        return max(timestamps)

    def get_attempted_count(self):
        """Get total number of attempted downloads"""
        return len(self.history)

    def clear_history(self):
        """Clear all history (use with caution)"""
        self.history = {}
        self._save_history()

    def remove_file(self, filename):
        """Remove a specific file from history"""
        if filename in self.history:
            del self.history[filename]
            self._save_history()
            return True
        return False
