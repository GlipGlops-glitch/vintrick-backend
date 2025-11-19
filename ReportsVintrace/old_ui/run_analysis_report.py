"""
Standalone script to download Analysis Report
Run: python ReportsVintrace/old_ui/run_analysis_report.py

Author: GlipGlops-glitch
Created: 2025-01-19
"""

import asyncio
from analysis_report import AnalysisReport


async def main():
    """Main function to download analysis report"""
    async with AnalysisReport(headless=False) as report:
        print("🔐 Logging in to Vintrace (Old UI)...")
        login_success = await report.login()
        
        if not login_success:
            print("❌ Login failed!")
            return
        
        print("\n📊 Downloading Analysis Report...")
        success = await report.download(
            start_date="08/01/2025",
            show_active_only=True
        )
        
        if success:
            print("\n✅ Analysis report downloaded successfully!")
        else:
            print("\n❌ Failed to download analysis report")


if __name__ == "__main__":
    asyncio.run(main())
