"""
Simple validation test for the refactored Analysis Report
Verifies imports and structure without requiring Playwright

Author: GlipGlops-glitch
Created: 2025-01-19
"""

def test_selector_imports():
    """Test that all selector imports work"""
    print("Testing Selector imports...")
    
    # Test old_ui direct imports
    from Selectors.old_ui import Common, Navigation, Reports
    assert hasattr(Common, 'Iframe')
    assert hasattr(Common, 'Loader')
    assert hasattr(Navigation, 'Nav')
    assert hasattr(Reports, 'Reports')
    print("  ✓ Direct old_ui imports work")
    
    # Test OldUI alias
    from Selectors import OldUI
    assert hasattr(OldUI, 'Common')
    assert hasattr(OldUI, 'Navigation')
    assert hasattr(OldUI, 'Reports')
    print("  ✓ OldUI alias works")
    
    # Test selector content
    from Selectors.old_ui.common import IframeSelectors, LoaderSelectors
    from Selectors.old_ui.navigation import NavigationSelectors
    from Selectors.old_ui.reports import ReportsSelectors
    
    assert len(IframeSelectors.IFRAME_MAIN) > 0
    assert len(NavigationSelectors.REPORTS_ICON) > 0
    assert len(ReportsSelectors.PRODUCT_ANALYSIS_CATEGORY) > 0
    assert len(ReportsSelectors.GENERATE_BUTTON) > 0
    assert len(ReportsSelectors.SHOW_ACTIVE_ONLY) > 0
    print("  ✓ Selector content is populated")
    
    print("✅ All selector imports passed!\n")


def test_config_imports():
    """Test that config imports work"""
    print("Testing Config imports...")
    
    from ReportsVintrace import config
    assert hasattr(config, 'DOWNLOAD_TIMEOUT')
    assert hasattr(config, 'SELECTOR_TIMEOUT')
    assert hasattr(config, 'OLD_URL')
    assert hasattr(config, 'LOGIN_URL')
    print("  ✓ Config module imports correctly")
    
    # Verify timeout values
    assert config.DOWNLOAD_TIMEOUT > 0
    assert config.SELECTOR_TIMEOUT > 0
    print("  ✓ Config values are set")
    
    print("✅ Config imports passed!\n")


def test_structure():
    """Test that the module structure is correct"""
    print("Testing module structure...")
    
    import os
    
    # Check that key files exist
    base_path = os.path.dirname(__file__)
    
    required_files = [
        'Selectors/old_ui/__init__.py',
        'Selectors/old_ui/common.py',
        'Selectors/old_ui/navigation.py',
        'Selectors/old_ui/reports.py',
        'ReportsVintrace/__init__.py',
        'ReportsVintrace/config.py',
        'ReportsVintrace/common/__init__.py',
        'ReportsVintrace/common/base_report.py',
        'ReportsVintrace/common/helpers.py',
        'ReportsVintrace/old_ui/__init__.py',
        'ReportsVintrace/old_ui/analysis_report.py',
        'ReportsVintrace/old_ui/run_analysis_report.py',
        'ReportsVintrace/README.md',
    ]
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        assert os.path.exists(full_path), f"Missing file: {file_path}"
        print(f"  ✓ {file_path}")
    
    print("✅ All required files exist!\n")


def test_tracking_import():
    """Test that tracking imports work"""
    print("Testing Tracking imports...")
    
    from Selectors.tracking import track_selector_attempt
    assert callable(track_selector_attempt)
    print("  ✓ track_selector_attempt is callable")
    
    print("✅ Tracking imports passed!\n")


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("VALIDATING REFACTORED ANALYSIS REPORT STRUCTURE")
    print("=" * 60 + "\n")
    
    try:
        test_structure()
        test_selector_imports()
        test_config_imports()
        test_tracking_import()
        
        print("=" * 60)
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("=" * 60)
        print("\nThe refactored Analysis Report structure is valid.")
        print("Note: Runtime testing requires Playwright to be installed.")
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
