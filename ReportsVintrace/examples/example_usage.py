"""
Example: Download Vintrace Reports
Shows how to use the ReportsVintrace system

Author: GlipGlops-glitch
Created: 2025-01-19

This script demonstrates various ways to use the ReportsVintrace package
to download reports from Vintrace.
"""

import asyncio
from ReportsVintrace.current_ui.vessels_report import VesselsReport
from ReportsVintrace.current_ui.barrel_report import BarrelReport


# ============================================================================
# EXAMPLE 1: Basic Usage with Context Manager
# ============================================================================

async def example_1_basic_vessels_report():
    """
    Simple example: Download vessel report using default settings.
    Credentials are loaded from .env file.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Vessels Report")
    print("=" * 70)

    async with VesselsReport(headless=False) as report:
        # Login (uses credentials from .env)
        if not await report.login():
            print("❌ Login failed")
            return

        # Download report (uses default filename and directory)
        if not await report.download():
            print("❌ Download failed")
            return

        print("✅ Report downloaded successfully!")


# ============================================================================
# EXAMPLE 2: Custom Configuration
# ============================================================================

async def example_2_custom_config():
    """
    Example with custom download directory and filename.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Custom Configuration")
    print("=" * 70)

    async with VesselsReport(
        headless=True,
        download_dir="my_custom_reports/"
    ) as report:
        await report.login()
        await report.download(output_filename="my_custom_vessels.csv")

        print("✅ Report downloaded to custom location!")


# ============================================================================
# EXAMPLE 3: Explicit Credentials
# ============================================================================

async def example_3_explicit_credentials():
    """
    Example using explicit credentials instead of .env file.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Explicit Credentials")
    print("=" * 70)

    async with BarrelReport(headless=False) as report:
        # Login with explicit credentials
        success = await report.login(
            username="user@example.com",  # Replace with actual credentials
            password="password123"
        )
        
        if success:
            await report.download()
            print("✅ Report downloaded!")
        else:
            print("❌ Login failed with provided credentials")


# ============================================================================
# EXAMPLE 4: Multiple Reports in Sequence
# ============================================================================

async def example_4_multiple_reports():
    """
    Download multiple reports in sequence.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Multiple Reports")
    print("=" * 70)

    # Download vessels report
    async with VesselsReport(headless=True) as vessels:
        await vessels.login()
        await vessels.download()
        print("✅ Vessels report complete")

    # Download barrels report
    async with BarrelReport(headless=True) as barrels:
        await barrels.login()
        await barrels.download()
        print("✅ Barrels report complete")

    print("✅ All reports downloaded!")


# ============================================================================
# EXAMPLE 5: Error Handling and Screenshots
# ============================================================================

async def example_5_error_handling():
    """
    Example with error handling and debug screenshots.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Error Handling")
    print("=" * 70)

    report = VesselsReport(headless=False)
    
    try:
        await report.init_browser()
        
        # Login
        login_success = await report.login()
        if not login_success:
            print("❌ Login failed, taking screenshot...")
            await report.screenshot("login_failure")
            return
        
        # Download
        download_success = await report.download()
        if not download_success:
            print("❌ Download failed, taking screenshot...")
            await report.screenshot("download_failure")
            return
        
        print("✅ Report downloaded successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        await report.screenshot("unexpected_error")
        
    finally:
        await report.cleanup()


# ============================================================================
# EXAMPLE 6: Without Context Manager (Manual Cleanup)
# ============================================================================

async def example_6_manual_cleanup():
    """
    Example without using context manager (manual cleanup).
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Manual Cleanup")
    print("=" * 70)

    report = VesselsReport(headless=False)
    
    try:
        # Manual initialization
        await report.init_browser()
        
        # Login and download
        await report.login()
        await report.download()
        
        print("✅ Report downloaded!")
        
    finally:
        # Manual cleanup
        await report.cleanup()


# ============================================================================
# EXAMPLE 7: Using Helper Methods
# ============================================================================

async def example_7_helper_methods():
    """
    Example using helper methods from the base class.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Helper Methods")
    print("=" * 70)

    async with VesselsReport(headless=False) as report:
        await report.login()
        
        # Wait for loaders
        print("⏳ Waiting for page to load...")
        await report.wait_for_loaders()
        
        # Take a screenshot
        screenshot_path = await report.screenshot("before_download")
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Track a selector manually
        report.track_success(
            selector_category="custom_action",
            selector="button.my-custom-button",
            success=True,
            context="example_script"
        )
        
        # Download report
        await report.download()
        
        print("✅ Report downloaded!")


# ============================================================================
# Main Function - Choose which example to run
# ============================================================================

async def main():
    """
    Run the examples.
    
    Uncomment the example you want to run.
    """
    
    # Choose one example to run:
    await example_1_basic_vessels_report()
    # await example_2_custom_config()
    # await example_3_explicit_credentials()
    # await example_4_multiple_reports()
    # await example_5_error_handling()
    # await example_6_manual_cleanup()
    # await example_7_helper_methods()
    
    print("\n" + "=" * 70)
    print("✅ Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
