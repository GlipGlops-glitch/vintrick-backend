"""
Selector Tracking Utility
Tracks successful selectors to optimize automation scripts

Author: GlipGlops-glitch
Created: 2025-01-10
Last Updated: 2025-01-10

This module logs successful selectors to a JSON file with metadata,
allowing you to analyze which selectors work best and optimize your code.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading

class SelectorTracker:
    """
    Tracks successful selector usage across Playwright automation runs.
    Thread-safe singleton implementation.
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
                # Fix: Use UTF-8 encoding
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
                "total_runs": 0
            },
            "selectors": {}
        }
    
    def _save_tracking_data(self):
        """Save tracking data to JSON file."""
        try:
            self.data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
            # Fix: Use UTF-8 encoding and ensure_ascii=False for Unicode characters
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Could not save tracking data: {e}")
    
    def track_success(
        self,
        function_name: str,
        selector: str,
        selector_type: str = "css",
        context: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """
        Track a successful selector usage.
        
        Args:
            function_name: Name of the function where selector was used
            selector: The actual selector string that worked
            selector_type: Type of selector (css, xpath, text, etc.)
            context: Additional context (e.g., "new_ui", "old_ui", "iframe")
            notes: Any additional notes about this selector
        """
        # Create unique key for this selector
        key = f"{function_name}::{selector}"
        
        if key not in self.data["selectors"]:
            self.data["selectors"][key] = {
                "function": function_name,
                "selector": selector,
                "type": selector_type,
                "context": context,
                "notes": notes,
                "first_seen": datetime.datetime.now().isoformat(),
                "last_seen": datetime.datetime.now().isoformat(),
                "success_count": 0,
                "attempts": []
            }
        
        # Update existing entry
        entry = self.data["selectors"][key]
        entry["last_seen"] = datetime.datetime.now().isoformat()
        entry["success_count"] += 1
        entry["attempts"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "success": True
        })
        
        # Keep only last 10 attempts to avoid file bloat
        if len(entry["attempts"]) > 10:
            entry["attempts"] = entry["attempts"][-10:]
        
        self._save_tracking_data()
    
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
        report.append("")
        
        # Group by function
        by_function = {}
        for key, entry in self.data["selectors"].items():
            func = entry["function"]
            if func not in by_function:
                by_function[func] = []
            by_function[func].append(entry)
        
        # Sort functions alphabetically
        for func in sorted(by_function.keys()):
            report.append(f"\n{'=' * 80}")
            report.append(f"Function: {func}")
            report.append('=' * 80)
            
            # Sort by success count (descending)
            entries = sorted(by_function[func], key=lambda x: x["success_count"], reverse=True)
            
            for entry in entries:
                report.append(f"\n  ✓ Selector: {entry['selector']}")
                report.append(f"    Type: {entry['type']}")
                report.append(f"    Success Count: {entry['success_count']}")
                report.append(f"    First Seen: {entry['first_seen']}")
                report.append(f"    Last Seen: {entry['last_seen']}")
                if entry.get('context'):
                    report.append(f"    Context: {entry['context']}")
                if entry.get('notes'):
                    report.append(f"    Notes: {entry['notes']}")
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)
    
    def get_best_selectors(self, function_name: Optional[str] = None) -> Dict:
        """
        Get the most successful selectors, optionally filtered by function.
        
        Args:
            function_name: Optional function name to filter by
            
        Returns:
            Dict: Selectors sorted by success count
        """
        selectors = self.data["selectors"]
        
        if function_name:
            selectors = {k: v for k, v in selectors.items() if v["function"] == function_name}
        
        # Sort by success count
        sorted_selectors = sorted(
            selectors.items(),
            key=lambda x: x[1]["success_count"],
            reverse=True
        )
        
        return dict(sorted_selectors)
    
    def increment_run_count(self):
        """Increment the total run counter."""
        self.data["metadata"]["total_runs"] += 1
        self._save_tracking_data()


# Global singleton instance
_tracker = SelectorTracker()


def track_selector(
    function_name: str,
    selector: str,
    selector_type: str = "css",
    context: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    Convenience function to track a successful selector.
    
    Usage:
        track_selector("vintrace_login", "input#email", "css", "new_ui", "Primary email field")
    """
    _tracker.track_success(function_name, selector, selector_type, context, notes)


def generate_selector_report() -> str:
    """Generate and return a selector usage report."""
    return _tracker.generate_report()


def save_selector_report(filename: str = "selector_report.txt"):
    """Save the selector report to a file with UTF-8 encoding."""
    report = generate_selector_report()
    # Fix: Specify UTF-8 encoding to handle Unicode characters (✓, ✗, etc.)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📊 Selector report saved to: {filename}")
    return filename


def get_best_selectors(function_name: Optional[str] = None) -> Dict:
    """Get the best performing selectors."""
    return _tracker.get_best_selectors(function_name)


def increment_run_count():
    """Increment the automation run counter."""
    _tracker.increment_run_count()


def print_tracking_summary():
    """Print a quick summary of tracking data."""
    print("\n" + "=" * 80)
    print("SELECTOR TRACKING SUMMARY")
    print("=" * 80)
    print(f"Total Selectors Tracked: {len(_tracker.data['selectors'])}")
    print(f"Total Runs: {_tracker.data['metadata']['total_runs']}")
    print(f"Last Updated: {_tracker.data['metadata']['last_updated']}")
    
    # Show top 5 selectors
    best = get_best_selectors()
    if best:
        print("\nTop 5 Most Successful Selectors:")
        for i, (key, data) in enumerate(list(best.items())[:5], 1):
            print(f"  {i}. {data['function']} - {data['selector'][:50]}... ({data['success_count']} uses)")
    
    print("=" * 80 + "\n")