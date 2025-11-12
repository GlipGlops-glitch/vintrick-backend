#  python tools/vintrace_Bulk_Stock_Report_playwright.py



import os
import shutil
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

def get_todays_date_str():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

REPORT_CONFIG = {
    "report_filename": f"vessel_contents_{get_todays_date_str()}.csv",
    "reports_icon_id": "c_170",  # reports quick launch icon
    "reports_icon_fallback": "div[title='Reports']",
    "tab_menu_id": "c_382|Text",   # Bulk wine tab span
    "csv_format_dropdown_id": "c_492",
    "csv_format_option_text": "CSV",
    "composition_checkbox_img_id": "c_419_stateicon", # first checkbox
    "origin_breakdown_dropdown_id": "c_458",
    "origin_breakdown_option_text": "Vintage / Grower / Vineyard / Block / Weigh tag# / Delivery date",
    "second_checkbox_img_id": "c_421_stateicon", # second checkbox
    "generate_btn_id": "c_414",
    "vintage_dropdown_id": "c_472",
    "vintage_option_text": "2025",
}

TARGET_SAVE_DIR = r"Main/data/vintrace_reports/"
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
TARGET_FILE_PATH = os.path.join(TARGET_SAVE_DIR, REPORT_CONFIG["report_filename"])
DOWNLOAD_TIMEOUT_MS = 120000

async def run():
    load_dotenv()
    USERNAME = os.getenv("VINTRACE_USER")
    PASSWORD = os.getenv("VINTRACE_PW")

    LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
    OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

            # Step 1: Login
            await page.goto(LOGIN_URL)
            await page.wait_for_selector("#email", timeout=60000)
            await page.fill("#email", USERNAME)
            await page.fill("#password", PASSWORD)
            login_btn = await page.query_selector("button[type='submit']:has-text('Login')")
            if login_btn:
                await login_btn.scroll_into_view_if_needed()
                await login_btn.click()
            else:
                print("Login button not found.")
            await page.wait_for_url(lambda url: url != LOGIN_URL, timeout=60000)

            # Step 2: Navigate to OLD_URL
            await page.goto(OLD_URL)
            print("Navigated to OLD_URL.")
            await page.wait_for_timeout(2000)  # Let the page load fully

            # Step 3: Click Reports icon (after login and navigation)
            reports_icon = await page.query_selector(f'#{REPORT_CONFIG["reports_icon_id"]}')
            if reports_icon:
                await reports_icon.scroll_into_view_if_needed()
                await reports_icon.click()
                print("Clicked the 'Reports' quick launch icon.")
            else:
                fallback_icon = await page.query_selector(REPORT_CONFIG['reports_icon_fallback'])
                if fallback_icon:
                    await fallback_icon.scroll_into_view_if_needed()
                    await fallback_icon.click()
                    print("Clicked the 'Reports' quick launch icon (fallback).")
                else:
                    print("Could not find Reports icon.")

            await page.wait_for_timeout(1000)

            # Step 4: Click Bulk wine tab (handle | in ID! Use fallback to text selector)
            try:
                tab = await page.query_selector(f'[id="{REPORT_CONFIG["tab_menu_id"]}"]')
                if tab:
                    await tab.scroll_into_view_if_needed()
                    await tab.click()
                    print("Clicked Bulk wine tab by ID.")
                else:
                    tab_by_text = await page.query_selector('span:text("Bulk wine")')
                    if tab_by_text:
                        await tab_by_text.scroll_into_view_if_needed()
                        await tab_by_text.click()
                        print("Clicked Bulk wine tab by text.")
                    else:
                        print("Bulk wine tab not found by ID or text.")
            except Exception as e:
                print(f"Error clicking Bulk wine tab: {e}")

            # Step 5: Select CSV format
            try:
                await page.wait_for_selector(f'#{REPORT_CONFIG["csv_format_dropdown_id"]}', timeout=8000)
                await page.select_option(f'#{REPORT_CONFIG["csv_format_dropdown_id"]}', label=REPORT_CONFIG["csv_format_option_text"])
                print("Selected CSV format in dropdown.")
            except Exception as e:
                print(f"Could not select CSV format: {e}")

            # Step 6: Click "Composition details" checkbox (first checkbox)
            try:
                await page.wait_for_selector(f'#{REPORT_CONFIG["composition_checkbox_img_id"]}', timeout=8000)
                await page.click(f'#{REPORT_CONFIG["composition_checkbox_img_id"]}')
                print("Clicked 'Composition details' checkbox.")
            except Exception as e:
                print(f"Could not click 'Composition details' checkbox: {e}")

            # Step 7: Select Origin Breakdown dropdown option
            try:
                await page.wait_for_selector(f'#{REPORT_CONFIG["origin_breakdown_dropdown_id"]}', timeout=8000)
                await page.select_option(f'#{REPORT_CONFIG["origin_breakdown_dropdown_id"]}', label=REPORT_CONFIG["origin_breakdown_option_text"])
                print("Selected Origin Breakdown option.")
            except Exception as e:
                print(f"Could not select Origin Breakdown option: {e}")

            # Step 8: Click second checkbox (after dropdowns)
            try:
                await page.wait_for_selector(f'#{REPORT_CONFIG["second_checkbox_img_id"]}', timeout=8000)
                await page.click(f'#{REPORT_CONFIG["second_checkbox_img_id"]}')
                print("Clicked second checkbox.")
            except Exception as e:
                print(f"Could not click second checkbox: {e}")

            # Step 9: Select Vintage year
            try:
                await page.wait_for_selector(f'#{REPORT_CONFIG["vintage_dropdown_id"]}', timeout=8000)
                await page.select_option(f'#{REPORT_CONFIG["vintage_dropdown_id"]}', label=REPORT_CONFIG["vintage_option_text"])
                print("Selected vintage dropdown option.")
            except Exception as e:
                print(f"Could not select vintage dropdown option: {e}")

            # Step 10: Click Generate button and download report
            try:
                await page.wait_for_selector(f'#{REPORT_CONFIG["generate_btn_id"]}', timeout=8000)
                async with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
                    await page.click(f'#{REPORT_CONFIG["generate_btn_id"]}')
                    print("Clicked 'Generate...' button.")
                download = await download_info.value
                temp_path = await download.path()
                if os.path.exists(TARGET_FILE_PATH):
                    os.remove(TARGET_FILE_PATH)
                shutil.move(temp_path, TARGET_FILE_PATH)
                print(f"Renamed and moved downloaded report to: {TARGET_FILE_PATH}")
            except Exception as e:
                print(f"Could not click the Generate button or download file: {e}")

    finally:
        if browser:
            await browser.close()

    print(f"Report should be downloaded and named: {TARGET_FILE_PATH}")

if __name__ == "__main__":
    asyncio.run(run())