"""
Selector Performance Tracking System
Tracks and analyzes selector success rates and performance

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

This module provides enhanced tracking capabilities for selector performance,
building upon the existing selector_tracker.py functionality.

Features:
- Track selector attempts (success/failure)
- Performance metrics (time to find, success rate)
- JSON storage with thread-safe writes
- Performance analytics and reporting
"""

import json
import os
import datetime
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class SelectorAttempt:
    """Record of a single selector attempt"""
    timestamp: str
    success: bool
    time_ms: float
    context: Optional[str] = None


@dataclass
class SelectorStats:
    """Statistics for a selector"""
    category: str
    selector: str
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    success_rate: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    first_seen: str
    last_seen: str
    last_success: Optional[str] = None
    last_failure: Optional[str] = None


class SelectorPerformanceTracker:
    """
    Thread-safe selector performance tracking system.
    Tracks success rates and timing metrics for all selectors.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, stats_file: Optional[str] = None):
        """Singleton pattern with thread safety"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, stats_file: Optional[str] = None):
        """Initialize the tracker with a stats file path"""
        if not hasattr(self, 'initialized'):
            # Default stats file location
            if stats_file is None:
                stats_dir = Path(__file__).parent
                stats_file = stats_dir / "selector_stats.json"
            
            self.stats_file = Path(stats_file)
            self.data = self._load_stats()
            self.write_lock = threading.Lock()
            self.initialized = True
    
    def _load_stats(self) -> Dict:
        """Load existing stats from JSON file"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠ Could not load stats: {e}")
                return self._init_stats_structure()
        return self._init_stats_structure()
    
    def _init_stats_structure(self) -> Dict:
        """Initialize the stats data structure"""
        return {
            "metadata": {
                "created": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "version": "1.0",
            },
            "selectors": {}
        }
    
    def _save_stats(self):
        """Thread-safe save to JSON file"""
        with self.write_lock:
            try:
                self.data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
                
                # Ensure directory exists
                self.stats_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write with UTF-8 encoding
                with open(self.stats_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"⚠ Could not save stats: {e}")
    
    def track_selector_attempt(
        self,
        category: str,
        selector: str,
        success: bool,
        time_ms: float,
        context: Optional[str] = None
    ):
        """
        Track a selector attempt with timing information.
        
        Args:
            category: Category of selector (e.g., 'export_button', 'iframe')
            selector: The actual selector string
            success: Whether the selector successfully found the element
            time_ms: Time taken to find element in milliseconds
            context: Additional context (e.g., 'new_ui', 'vessels_page')
        """
        key = f"{category}::{selector}"
        timestamp = datetime.datetime.now().isoformat()
        
        if key not in self.data["selectors"]:
            self.data["selectors"][key] = {
                "category": category,
                "selector": selector,
                "total_attempts": 0,
                "successful_attempts": 0,
                "failed_attempts": 0,
                "times_ms": [],
                "first_seen": timestamp,
                "last_seen": timestamp,
                "last_success": None,
                "last_failure": None,
                "attempts": []
            }
        
        entry = self.data["selectors"][key]
        entry["total_attempts"] += 1
        entry["last_seen"] = timestamp
        
        if success:
            entry["successful_attempts"] += 1
            entry["last_success"] = timestamp
        else:
            entry["failed_attempts"] += 1
            entry["last_failure"] = timestamp
        
        entry["times_ms"].append(time_ms)
        
        # Store attempt details (keep last 50 to avoid bloat)
        attempt = {
            "timestamp": timestamp,
            "success": success,
            "time_ms": time_ms,
            "context": context
        }
        entry["attempts"].append(attempt)
        if len(entry["attempts"]) > 50:
            entry["attempts"] = entry["attempts"][-50:]
        
        self._save_stats()
    
    def get_best_selectors(self, category: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get top performing selectors for a category.
        
        Args:
            category: Selector category to filter by
            limit: Maximum number of selectors to return
            
        Returns:
            List of selector stats dictionaries, sorted by performance
        """
        category_selectors = []
        
        for key, entry in self.data["selectors"].items():
            if entry["category"] == category:
                # Calculate success rate
                total = entry["total_attempts"]
                success = entry["successful_attempts"]
                success_rate = success / total if total > 0 else 0
                
                # Calculate average time
                times = entry["times_ms"]
                avg_time = sum(times) / len(times) if times else 0
                
                category_selectors.append({
                    "selector": entry["selector"],
                    "success_rate": success_rate,
                    "avg_time_ms": avg_time,
                    "total_attempts": total,
                    "successful_attempts": success,
                    "failed_attempts": entry["failed_attempts"],
                })
        
        # Sort by success rate (descending), then by avg time (ascending)
        category_selectors.sort(
            key=lambda x: (-x["success_rate"], x["avg_time_ms"])
        )
        
        return category_selectors[:limit]
    
    def get_selector_stats(self, category: str) -> Dict[str, SelectorStats]:
        """
        Get detailed statistics for all selectors in a category.
        
        Args:
            category: Selector category to get stats for
            
        Returns:
            Dictionary mapping selector strings to SelectorStats objects
        """
        stats = {}
        
        for key, entry in self.data["selectors"].items():
            if entry["category"] == category:
                times = entry["times_ms"]
                total = entry["total_attempts"]
                success = entry["successful_attempts"]
                
                stats[entry["selector"]] = SelectorStats(
                    category=category,
                    selector=entry["selector"],
                    total_attempts=total,
                    successful_attempts=success,
                    failed_attempts=entry["failed_attempts"],
                    success_rate=success / total if total > 0 else 0,
                    avg_time_ms=sum(times) / len(times) if times else 0,
                    min_time_ms=min(times) if times else 0,
                    max_time_ms=max(times) if times else 0,
                    first_seen=entry["first_seen"],
                    last_seen=entry["last_seen"],
                    last_success=entry.get("last_success"),
                    last_failure=entry.get("last_failure"),
                )
        
        return stats
    
    def export_stats_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a human-readable performance report.
        
        Args:
            output_file: Optional file path to save report
            
        Returns:
            The report as a string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("SELECTOR PERFORMANCE REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.datetime.now().isoformat()}")
        lines.append(f"Total Selectors Tracked: {len(self.data['selectors'])}")
        lines.append("")
        
        # Group by category
        by_category = {}
        for key, entry in self.data["selectors"].items():
            cat = entry["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(entry)
        
        # Report each category
        for category in sorted(by_category.keys()):
            lines.append("")
            lines.append("=" * 80)
            lines.append(f"Category: {category}")
            lines.append("=" * 80)
            
            # Sort by success rate
            entries = by_category[category]
            for entry in entries:
                total = entry["total_attempts"]
                success = entry["successful_attempts"]
                success_rate = (success / total * 100) if total > 0 else 0
                
                times = entry["times_ms"]
                avg_time = sum(times) / len(times) if times else 0
                
                lines.append(f"\n  Selector: {entry['selector']}")
                lines.append(f"    Success Rate: {success_rate:.1f}% ({success}/{total} attempts)")
                lines.append(f"    Avg Time: {avg_time:.2f}ms")
                lines.append(f"    First Seen: {entry['first_seen']}")
                lines.append(f"    Last Seen: {entry['last_seen']}")
                
                if entry.get("last_success"):
                    lines.append(f"    Last Success: {entry['last_success']}")
                if entry.get("last_failure"):
                    lines.append(f"    Last Failure: {entry['last_failure']}")
        
        lines.append("\n" + "=" * 80)
        
        report = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📊 Performance report saved to: {output_file}")
        
        return report


# Global singleton instance
_tracker = SelectorPerformanceTracker()


# Convenience functions
def track_selector_attempt(
    category: str,
    selector: str,
    success: bool,
    time_ms: float,
    context: Optional[str] = None
):
    """
    Track a selector attempt.
    
    Usage:
        track_selector_attempt(
            category="export_button",
            selector="button#exportBtn",
            success=True,
            time_ms=125.5,
            context="vessels_page"
        )
    """
    _tracker.track_selector_attempt(category, selector, success, time_ms, context)


def get_best_selectors(category: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Get top performing selectors for a category."""
    return _tracker.get_best_selectors(category, limit)


def get_selector_stats(category: str) -> Dict[str, SelectorStats]:
    """Get detailed statistics for a category."""
    return _tracker.get_selector_stats(category)


def export_stats_report(output_file: Optional[str] = None) -> str:
    """Generate and optionally save a performance report."""
    return _tracker.export_stats_report(output_file)
