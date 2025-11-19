#!/usr/bin/env python3
"""
Basic tests for the Selector Management System

Run with: python -m pytest Selectors/test_selectors.py -v
Or simply: python Selectors/test_selectors.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported"""
    from Selectors import NewUI
    from Selectors import track_selector_attempt, get_best_selectors
    from Selectors import get_selector_list, validate_selector_format
    print("✓ All imports successful")


def test_selector_access():
    """Test accessing selectors from organized structure"""
    from Selectors import NewUI
    
    # Test Common selectors
    assert len(NewUI.Common.Iframe.IFRAME_MAIN) == 3
    assert len(NewUI.Common.Loader.LOADER_DIVS) == 1
    assert len(NewUI.Common.Loader.LOADING_INDICATORS) == 4
    assert len(NewUI.Common.Popup.CLOSE_BUTTONS) == 8
    
    # Test Navigation selectors
    assert len(NewUI.Navigation.Menu.REPORTS_MENU) == 5
    
    # Test Export selectors
    assert len(NewUI.Export.Button.EXPORT_BUTTON) == 3
    assert len(NewUI.Export.Menu.EXCEL_MENU_ITEM) == 5
    assert len(NewUI.Export.Menu.EXCEL_ALL_OPTION) == 5
    assert len(NewUI.Export.Menu.BARREL_DETAILS_MENU_ITEM) == 3
    assert len(NewUI.Export.Menu.BARREL_DETAILS_ALL_OPTION) == 3
    
    # Test Report selectors
    assert len(NewUI.Reports.Category.VINTAGE_HARVEST_TAB) == 5
    assert len(NewUI.Reports.Category.PRODUCT_ANALYSIS_CATEGORY) == 4
    assert len(NewUI.Reports.Control.SHOW_ACTIVE_ONLY) == 3
    assert len(NewUI.Reports.Control.GENERATE_BUTTON) == 4
    
    print("✓ All selector counts verified")


def test_tracking_functions():
    """Test performance tracking functionality"""
    from Selectors import track_selector_attempt, get_best_selectors
    
    # Track a test selector
    track_selector_attempt(
        category="test_category",
        selector="test_selector",
        success=True,
        time_ms=100.0,
        context="test_context"
    )
    
    # Retrieve best selectors
    best = get_best_selectors("test_category", limit=1)
    assert len(best) >= 1
    assert best[0]["selector"] == "test_selector"
    assert best[0]["success_rate"] == 1.0
    
    print("✓ Tracking functions working")


def test_utility_functions():
    """Test utility functions"""
    from Selectors import (
        validate_selector_format,
        merge_selector_lists,
        get_selector_type,
        get_selector_list,
        NewUI
    )
    
    # Test validation
    assert validate_selector_format("button#myBtn") == True
    assert validate_selector_format("") == False
    assert validate_selector_format("   ") == False
    
    # Test merging
    result = merge_selector_lists(["a", "b"], ["b", "c"])
    assert result == ["a", "b", "c"]
    
    # Test selector type detection
    assert get_selector_type("button#btn") == "css"
    assert get_selector_type("//button[@id='btn']") == "xpath"
    assert get_selector_type("text=Click me") == "text"
    
    # Test get_selector_list
    selectors = get_selector_list(NewUI.Common.Iframe, 'IFRAME_MAIN')
    assert len(selectors) == 3
    
    print("✓ Utility functions working")


def test_backward_compatibility():
    """Test backward compatibility with old selector system"""
    from tools.vintrace_selectors import NewUISelectors
    from Selectors import NewUI
    
    # Compare old and new
    assert NewUISelectors.IFRAME_MAIN == NewUI.Common.Iframe.IFRAME_MAIN
    assert NewUISelectors.EXPORT_BUTTON == NewUI.Export.Button.EXPORT_BUTTON
    assert NewUISelectors.REPORTS_MENU == NewUI.Navigation.Menu.REPORTS_MENU
    assert NewUISelectors.EXCEL_MENU_ITEM == NewUI.Export.Menu.EXCEL_MENU_ITEM
    assert NewUISelectors.EXCEL_ALL_OPTION == NewUI.Export.Menu.EXCEL_ALL_OPTION
    
    print("✓ Backward compatibility verified")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("Running Selector Management System Tests")
    print("=" * 80)
    
    tests = [
        ("Import Test", test_imports),
        ("Selector Access Test", test_selector_access),
        ("Tracking Functions Test", test_tracking_functions),
        ("Utility Functions Test", test_utility_functions),
        ("Backward Compatibility Test", test_backward_compatibility),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n{name}...")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {name} FAILED: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
