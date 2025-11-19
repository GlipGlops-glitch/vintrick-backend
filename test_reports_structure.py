#!/usr/bin/env python3
"""
Basic Import and Structure Test for ReportsVintrace

This test validates that all modules can be imported correctly
and that the basic structure is sound.

Note: This does NOT test actual functionality (requires Playwright and credentials).
It only validates syntax and import structure.

Run with: python3 test_reports_structure.py
"""

import sys
import traceback


def test_selectors_import():
    """Test that Selectors package imports correctly."""
    print("\n" + "=" * 70)
    print("TEST: Selectors Package Import")
    print("=" * 70)
    
    try:
        import Selectors
        print("✓ Selectors package imports")
        
        from Selectors.tracking import track_selector_attempt
        print("✓ track_selector_attempt function imports")
        
        from Selectors.common import LoginSelectors, PopupSelectors
        print("✓ Common selectors import")
        
        from Selectors.new_ui.common import IframeSelectors, LoaderSelectors
        print("✓ New UI common selectors import")
        
        from Selectors.new_ui.export import ExportSelectors
        print("✓ New UI export selectors import")
        
        from Selectors.old_ui.reports import ReportSelectors
        print("✓ Old UI report selectors import")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        traceback.print_exc()
        return False


def test_reports_vintrace_import():
    """Test that ReportsVintrace package imports correctly."""
    print("\n" + "=" * 70)
    print("TEST: ReportsVintrace Package Import")
    print("=" * 70)
    
    try:
        import ReportsVintrace
        print("✓ ReportsVintrace package imports")
        
        from ReportsVintrace import config
        print("✓ Config module imports")
        
        # Note: These will fail if playwright is not installed
        # but we can at least check if the module exists
        try:
            from ReportsVintrace.common.base_report import VintraceReport
            print("✓ VintraceReport base class imports")
            print("  (Playwright is installed)")
        except ModuleNotFoundError as e:
            if 'playwright' in str(e):
                print("⚠ VintraceReport requires Playwright (not installed)")
                print("  This is expected in environments without Playwright")
            else:
                raise
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        traceback.print_exc()
        return False


def test_selector_values():
    """Test that selector values are properly defined."""
    print("\n" + "=" * 70)
    print("TEST: Selector Values")
    print("=" * 70)
    
    try:
        from Selectors.common import LoginSelectors
        assert isinstance(LoginSelectors.EMAIL_INPUT, list)
        assert len(LoginSelectors.EMAIL_INPUT) > 0
        print(f"✓ LoginSelectors.EMAIL_INPUT has {len(LoginSelectors.EMAIL_INPUT)} selectors")
        
        from Selectors.new_ui.export import ExportSelectors
        assert isinstance(ExportSelectors.EXPORT_BUTTON, list)
        assert len(ExportSelectors.EXPORT_BUTTON) > 0
        print(f"✓ ExportSelectors.EXPORT_BUTTON has {len(ExportSelectors.EXPORT_BUTTON)} selectors")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        traceback.print_exc()
        return False


def test_config_values():
    """Test that config values are properly defined."""
    print("\n" + "=" * 70)
    print("TEST: Configuration Values")
    print("=" * 70)
    
    try:
        from ReportsVintrace import config
        
        assert hasattr(config, 'DEFAULT_DOWNLOAD_DIRS')
        assert isinstance(config.DEFAULT_DOWNLOAD_DIRS, dict)
        print(f"✓ DEFAULT_DOWNLOAD_DIRS defined with {len(config.DEFAULT_DOWNLOAD_DIRS)} entries")
        
        assert hasattr(config, 'DOWNLOAD_TIMEOUT')
        assert isinstance(config.DOWNLOAD_TIMEOUT, int)
        print(f"✓ DOWNLOAD_TIMEOUT = {config.DOWNLOAD_TIMEOUT}ms")
        
        assert hasattr(config, 'LOGIN_URL')
        assert isinstance(config.LOGIN_URL, str)
        print(f"✓ LOGIN_URL defined")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("REPORTSVINTRRACE STRUCTURE VALIDATION")
    print("=" * 70)
    print("\nThis test validates package structure and imports.")
    print("It does NOT test actual functionality (requires Playwright).")
    
    results = []
    
    # Run tests
    results.append(("Selectors Import", test_selectors_import()))
    results.append(("ReportsVintrace Import", test_reports_vintrace_import()))
    results.append(("Selector Values", test_selector_values()))
    results.append(("Config Values", test_config_values()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All structure tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
