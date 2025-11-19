#!/usr/bin/env python3
"""
Demo script showing how to use the new Selector Management System

This script demonstrates:
1. Importing selectors
2. Using selectors with performance tracking
3. Getting best performing selectors
4. Generating performance reports
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import Selectors
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from Selectors import (
    NewUI,
    track_selector_attempt,
    get_best_selectors,
    get_prioritized_selectors,
    export_stats_report,
    validate_selector_format,
)


def demo_basic_usage():
    """Demonstrate basic selector access"""
    print("=" * 80)
    print("DEMO: Basic Selector Access")
    print("=" * 80)
    
    # Access iframe selectors
    iframe_selectors = NewUI.Common.Iframe.IFRAME_MAIN
    print(f"\n✓ Iframe Selectors ({len(iframe_selectors)} variants):")
    for i, sel in enumerate(iframe_selectors, 1):
        print(f"  {i}. {sel}")
    
    # Access export button selectors
    export_selectors = NewUI.Export.Button.EXPORT_BUTTON
    print(f"\n✓ Export Button Selectors ({len(export_selectors)} variants):")
    for i, sel in enumerate(export_selectors, 1):
        print(f"  {i}. {sel}")
    
    # Access navigation selectors
    reports_menu = NewUI.Navigation.Menu.REPORTS_MENU
    print(f"\n✓ Reports Menu Selectors ({len(reports_menu)} variants):")
    for i, sel in enumerate(reports_menu, 1):
        print(f"  {i}. {sel}")


def demo_tracking():
    """Demonstrate performance tracking"""
    print("\n" + "=" * 80)
    print("DEMO: Performance Tracking")
    print("=" * 80)
    
    # Simulate trying multiple selectors
    test_selectors = [
        ("button#exportBtn", True, 125.5),
        ("button.export-btn", False, 200.0),
        ("button[data-action='export']", True, 150.0),
        ("button#exportBtn", True, 115.2),  # Same selector works again
    ]
    
    print("\n✓ Tracking selector attempts...")
    for selector, success, time_ms in test_selectors:
        track_selector_attempt(
            category="export_button",
            selector=selector,
            success=success,
            time_ms=time_ms,
            context="demo_vessels_page"
        )
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {status}: {selector} ({time_ms:.1f}ms)")
    
    # Get best performers
    print("\n✓ Best performing selectors:")
    best = get_best_selectors("export_button", limit=3)
    for i, sel_info in enumerate(best, 1):
        print(f"  {i}. {sel_info['selector']}")
        print(f"     Success Rate: {sel_info['success_rate']:.1%}")
        print(f"     Avg Time: {sel_info['avg_time_ms']:.1f}ms")
        print(f"     Attempts: {sel_info['total_attempts']}")


def demo_utilities():
    """Demonstrate utility functions"""
    print("\n" + "=" * 80)
    print("DEMO: Utility Functions")
    print("=" * 80)
    
    # Validate selectors
    print("\n✓ Selector Validation:")
    test_cases = [
        "button#myBtn",
        "",
        "//div[@class='test']",
        "text=Click me",
    ]
    for selector in test_cases:
        valid = validate_selector_format(selector)
        status = "✓" if valid else "✗"
        display = selector if selector else "(empty)"
        print(f"  {status} {display}")
    
    # Get prioritized selectors
    print("\n✓ Prioritized Selectors (by performance):")
    prioritized = get_prioritized_selectors("export_button", ui_version="new")
    for i, sel in enumerate(prioritized, 1):
        print(f"  {i}. {sel}")


def demo_report():
    """Generate and display performance report"""
    print("\n" + "=" * 80)
    print("DEMO: Performance Report")
    print("=" * 80)
    
    report = export_stats_report()
    print("\n" + report)


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("Vintrace Selector Management System - Demo")
    print("=" * 80)
    
    demo_basic_usage()
    demo_tracking()
    demo_utilities()
    demo_report()
    
    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Check Selectors/tracking/selector_stats.json for raw data")
    print("2. Import selectors in your automation scripts")
    print("3. Track performance during real automation runs")
    print("4. Review Selectors/README.md for full documentation")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
