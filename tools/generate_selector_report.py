#!/usr/bin/env python3
"""
Generate a report of tracked selectors.
Run this after your automation scripts to see which selectors are working.

Usage:
    python generate_selector_report.py
"""

from selector_tracker import save_selector_report, get_best_selectors, generate_selector_report
import sys
import json

def main():
    print("Generating selector tracking report...\n")
    
    # Print to console
    report = generate_selector_report()
    print(report)
    
    # Save to file
    save_selector_report("selector_report.txt")
    
    # Also save raw JSON for easy copy-paste
    print("\n📋 Full tracking data saved to: selector_tracking.json")
    print("📄 Human-readable report saved to: selector_report.txt")
    
    # Show top 10 most successful selectors
    print("\n" + "=" * 80)
    print("TOP 10 MOST SUCCESSFUL SELECTORS")
    print("=" * 80)
    
    best = get_best_selectors()
    for i, (key, data) in enumerate(list(best.items())[:10], 1):
        print(f"\n{i}. {data['function']}")
        print(f"   Selector: {data['selector']}")
        print(f"   Success Count: {data['success_count']}")
        print(f"   Type: {data['type']}")
        if data.get('context'):
            print(f"   Context: {data['context']}")
    
    # Print instructions for next steps
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Review the selector_report.txt file")
    print("2. Copy the contents of selector_tracking.json")
    print("3. Paste it back to GitHub Copilot for optimization suggestions")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)