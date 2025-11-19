"""
Selector Tracking System
Tracks selector usage and success rates to optimize automation scripts

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

This module provides the track_selector_attempt function that all report scripts
should use to log selector attempts, helping the system learn which selectors
work best over time.
"""

import json
import os
import datetime
from typing import Optional, Dict, Any
import threading
from pathlib import Path


class SelectorTracker:
    """
    Tracks successful and failed selector attempts across Playwright automation runs.
    Thread-safe singleton implementation that learns which selectors work best.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.tracking_file = "selector_tracking.json"
            self.data = self._load_tracking_data()
            self.initialized = True

    def _load_tracking_data(self) -> Dict:
        """Load existing tracking data from JSON file."""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠ Could not load tracking data: {e}")
                return self._init_tracking_structure()
        return self._init_tracking_structure()

    def _init_tracking_structure(self) -> Dict:
        """Initialize the tracking data structure."""
        return {
            "metadata": {
                "created": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "total_attempts": 0,
                "total_successes": 0,
                "version": "2.0.0"
            },
            "selectors": {}
        }

    def _save_tracking_data(self):
        """Save tracking data to JSON file."""
        try:
            self.data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Could not save tracking data: {e}")

    def track_attempt(
        self,
        category: str,
        selector: str,
        success: bool,
        time_ms: Optional[float] = None,
        context: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """
        Track a selector attempt (success or failure).

        Args:
            category: Category of selector (e.g., 'export_button', 'login_email')
            selector: The actual selector string that was tried
            success: Whether the selector worked
            time_ms: Time taken in milliseconds (optional)
            context: Additional context (e.g., "new_ui", "old_ui", "iframe")
            notes: Any additional notes about this attempt
        """
        # Create unique key for this selector
        key = f"{category}::{selector}"

        if key not in self.data["selectors"]:
            self.data["selectors"][key] = {
                "category": category,
                "selector": selector,
                "context": context,
                "notes": notes,
                "first_seen": datetime.datetime.now().isoformat(),
                "last_seen": datetime.datetime.now().isoformat(),
                "success_count": 0,
                "failure_count": 0,
                "total_time_ms": 0.0,
                "avg_time_ms": 0.0,
                "attempts": []
            }

        # Update existing entry
        entry = self.data["selectors"][key]
        entry["last_seen"] = datetime.datetime.now().isoformat()
        
        if success:
            entry["success_count"] += 1
            self.data["metadata"]["total_successes"] += 1
        else:
            entry["failure_count"] += 1
        
        self.data["metadata"]["total_attempts"] += 1

        # Track timing if provided
        if time_ms is not None:
            entry["total_time_ms"] += time_ms
            if entry["success_count"] > 0:
                entry["avg_time_ms"] = entry["total_time_ms"] / entry["success_count"]

        # Record attempt
        attempt_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "success": success,
        }
        if time_ms is not None:
            attempt_record["time_ms"] = time_ms
        
        entry["attempts"].append(attempt_record)

        # Keep only last 10 attempts to avoid file bloat
        if len(entry["attempts"]) > 10:
            entry["attempts"] = entry["attempts"][-10:]

        self._save_tracking_data()

    def get_best_selectors(self, category: Optional[str] = None) -> list:
        """
        Get the most successful selectors, optionally filtered by category.

        Args:
            category: Optional category to filter by

        Returns:
            list: Selectors sorted by success rate and count
        """
        selectors = self.data["selectors"]

        if category:
            selectors = {k: v for k, v in selectors.items() if v["category"] == category}

        # Sort by success rate (success / total attempts) and then by success count
        sorted_selectors = sorted(
            selectors.items(),
            key=lambda x: (
                x[1]["success_count"] / max(x[1]["success_count"] + x[1]["failure_count"], 1),
                x[1]["success_count"]
            ),
            reverse=True
        )

        return [
            {
                "category": v["category"],
                "selector": v["selector"],
                "success_count": v["success_count"],
                "failure_count": v["failure_count"],
                "success_rate": v["success_count"] / max(v["success_count"] + v["failure_count"], 1),
                "avg_time_ms": v.get("avg_time_ms", 0),
            }
            for k, v in sorted_selectors
        ]

    def generate_report(self) -> str:
        """
        Generate a human-readable report of selector usage.

        Returns:
            str: Formatted report text
        """
        report = []
        report.append("=" * 80)
        report.append("SELECTOR TRACKING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.datetime.now().isoformat()}")
        report.append(f"Total Tracked Selectors: {len(self.data['selectors'])}")
        report.append(f"Total Attempts: {self.data['metadata']['total_attempts']}")
        report.append(f"Total Successes: {self.data['metadata']['total_successes']}")
        report.append("")

        # Group by category
        by_category = {}
        for key, entry in self.data["selectors"].items():
            cat = entry["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(entry)

        # Sort categories alphabetically
        for cat in sorted(by_category.keys()):
            report.append(f"\n{'=' * 80}")
            report.append(f"Category: {cat}")
            report.append('=' * 80)

            # Sort by success rate
            entries = sorted(
                by_category[cat],
                key=lambda x: x["success_count"] / max(x["success_count"] + x["failure_count"], 1),
                reverse=True
            )

            for entry in entries:
                total = entry["success_count"] + entry["failure_count"]
                success_rate = (entry["success_count"] / total * 100) if total > 0 else 0
                
                report.append(f"\n  Selector: {entry['selector']}")
                report.append(f"    Success Rate: {success_rate:.1f}% ({entry['success_count']}/{total})")
                report.append(f"    Avg Time: {entry.get('avg_time_ms', 0):.1f}ms")
                report.append(f"    First Seen: {entry['first_seen']}")
                report.append(f"    Last Seen: {entry['last_seen']}")
                if entry.get('context'):
                    report.append(f"    Context: {entry['context']}")
                if entry.get('notes'):
                    report.append(f"    Notes: {entry['notes']}")

        report.append("\n" + "=" * 80)
        return "\n".join(report)


# Global singleton instance
_tracker = SelectorTracker()


def track_selector_attempt(
    category: str,
    selector: str,
    success: bool,
    time_ms: Optional[float] = None,
    context: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    Track a selector attempt for learning and optimization.

    This function should be called after every selector attempt (successful or not)
    to help the system learn which selectors work best.

    Args:
        category: Category of selector (e.g., 'export_button', 'login_email')
        selector: The actual selector string that was tried
        success: Whether the selector worked
        time_ms: Time taken in milliseconds (optional)
        context: Additional context (e.g., "new_ui", "old_ui", "iframe")
        notes: Any additional notes about this attempt

    Example:
        >>> track_selector_attempt(
        ...     category="login_email",
        ...     selector="input#email",
        ...     success=True,
        ...     time_ms=150.5,
        ...     context="new_ui",
        ...     notes="Primary email input field"
        ... )
    """
    _tracker.track_attempt(category, selector, success, time_ms, context, notes)


def get_best_selectors(category: Optional[str] = None) -> list:
    """
    Get the best performing selectors.

    Args:
        category: Optional category to filter by

    Returns:
        list: List of selector performance data
    """
    return _tracker.get_best_selectors(category)


def generate_selector_report() -> str:
    """Generate and return a selector usage report."""
    return _tracker.generate_report()


def save_selector_report(filename: str = "selector_report.txt"):
    """Save the selector report to a file."""
    report = generate_selector_report()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📊 Selector report saved to: {filename}")
    return filename
