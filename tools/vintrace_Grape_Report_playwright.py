#  python tools/vintrace_Grape_Report_playwright.py
import os
import shutil
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load credentials from .env
load_dotenv()
USERNAME = os.getenv("VINTRACE_USER")
PASSWORD = os.getenv("VINTRACE_PW")

LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

REPORT_FILENAME = "grape_delivery_report.csv"
TARGET_SAVE_DIR = r"Main/data/vintrace_reports/"
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
TARGET_FILE_PATH = os.path.join(TARGET_SAVE_DIR, REPORT_FILENAME)

DOWNLOAD_TIMEOUT_MS = 120000  # 2 minutes

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        # Step 1: Go to login page
        await page.goto(LOGIN_URL)

        # Step 2: Log in using HTML fields provided
        await page.fill('input#email', USERNAME)
        await asyncio.sleep(1)
        await page.fill('input#password', PASSWORD)
        await asyncio.sleep(1)
        login_btn = await page.query_selector("button[type='submit']:has-text('Login')")
        if login_btn:
            await login_btn.scroll_into_view_if_needed()
            await login_btn.click()
        else:
            print("Login button not found.")

        # Step 3: Wait for login to complete
        await page.wait_for_url(lambda url: url != LOGIN_URL, timeout=60000)

        # Step 4: Navigate to OLD_URL (the old Vintrace UI)
        await page.goto(OLD_URL)
        print("Navigated to OLD_URL.")
        await asyncio.sleep(2)

        # Step 5: Click on Reports quick launch icon by ID or title
        reports_clicked = False
        try:
            await page.wait_for_selector("#c_170", timeout=10000)
            reports_icon = await page.query_selector("#c_170")
            if reports_icon:
                await reports_icon.scroll_into_view_if_needed()
                await reports_icon.click()
                print("Clicked the 'Reports' quick launch icon by ID.")
                reports_clicked = True
        except Exception as e:
            print(f"Could not click Reports icon by ID: {e}")
        if not reports_clicked:
            try:
                await page.wait_for_selector("div[title='Reports']", timeout=10000)
                reports_icon = await page.query_selector("div[title='Reports']")
                if reports_icon:
                    await reports_icon.scroll_into_view_if_needed()
                    await reports_icon.click()
                    print("Clicked the 'Reports' quick launch icon by title.")
            except Exception as e2:
                print(f"Could not click Reports icon by title: {e2}")

        await asyncio.sleep(1)

        # Step 6: Click on Vintage/Harvest tab/menu
        vintage_clicked = False
        try:
            await page.wait_for_selector("#c_384\\|Text", timeout=10000)
            vintage_tab = await page.query_selector("#c_384\\|Text")
            if vintage_tab:
                await vintage_tab.scroll_into_view_if_needed()
                await vintage_tab.click()
                print("Clicked 'Vintage/Harvest' by ID.")
                vintage_clicked = True
        except Exception as e:
            print(f"Could not click Vintage/Harvest by ID: {e}")
        if not vintage_clicked:
            try:
                await page.wait_for_selector("span:text('Vintage/Harvest')", timeout=10000)
                vintage_tab = await page.query_selector("span:text('Vintage/Harvest')")
                if vintage_tab:
                    await vintage_tab.scroll_into_view_if_needed()
                    await vintage_tab.click()
                    print("Clicked 'Vintage/Harvest' by text.")
                    vintage_clicked = True
            except Exception as e2:
                print(f"Could not click Vintage/Harvest by text: {e2}")
        if not vintage_clicked:
            try:
                vintage_span = await page.query_selector("#c_384\\|Text")
                if vintage_span:
                    parent = await vintage_span.evaluate_handle("el => el.parentElement")
                    await parent.scroll_into_view_if_needed()
                    await parent.click()
                    print("Clicked parent of 'Vintage/Harvest' span.")
            except Exception as e3:
                print(f"Could not click parent of Vintage/Harvest span: {e3}")

        # Step 7: Select "CSV" from the correct table dropdown
        try:
            await page.wait_for_selector("#c_600", timeout=10000)
            csv_dropdown = await page.query_selector("#c_600")
            if csv_dropdown:
                await csv_dropdown.scroll_into_view_if_needed()
                await page.select_option("#c_600", label="CSV")
                print("Selected 'CSV' from the table dropdown.")
            else:
                print("CSV dropdown not found.")
        except Exception as e:
            print(f"Could not select 'CSV' from table dropdown: {e}")

        # Step 8: Select "2025" from the correct vintage dropdown (using precise ID from your HTML)
        try:
            await page.wait_for_selector("#c_451", timeout=10000)
            vintage_dropdown = await page.query_selector("#c_451")
            if vintage_dropdown:
                await vintage_dropdown.scroll_into_view_if_needed()
                await page.select_option("#c_451", label="2025")
                print("Selected '2025' from the vintage dropdown.")
            else:
                print("Vintage dropdown not found.")
        except Exception as e:
            print(f"Could not select '2025' from vintage dropdown: {e}")

        # Step 9: Click the "Generate..." button to run the report and wait for download (longer timeout)
        try:
            await page.wait_for_selector("#c_517", timeout=10000)
            generate_btn = await page.query_selector("#c_517")
            if generate_btn:
                await generate_btn.scroll_into_view_if_needed()
                async with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
                    await generate_btn.click()
                    print("Clicked the 'Generate...' button to run the report.")

                download = await download_info.value
                temp_path = await download.path()
                # Rename/move as before
                if download.suggested_filename.startswith("VINx2_DeliveryReport_2025") and download.suggested_filename.lower().endswith('.csv'):
                    if os.path.exists(TARGET_FILE_PATH):
                        os.remove(TARGET_FILE_PATH)
                    shutil.move(temp_path, TARGET_FILE_PATH)
                    print(f"Renamed and moved downloaded report to: {TARGET_FILE_PATH}")
                else:
                    print(f"Unexpected download filename: {download.suggested_filename}")
            else:
                print("Generate button not found.")
        except Exception as e:
            print(f"Error downloading report: {e}")

        await browser.close()

    print(f"Report should be downloaded and named: {TARGET_FILE_PATH}")

if __name__ == "__main__":
    asyncio.run(run())