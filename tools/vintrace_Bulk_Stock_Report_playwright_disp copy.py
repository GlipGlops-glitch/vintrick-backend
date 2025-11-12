#  python tools/vintrace_Bulk_Stock_Report_playwright_disp.py


import os
import shutil
import csv
import json
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

CSV_INPUT_PATH = r"Main/data/vintrace_reports/dispatch_report.csv"
TARGET_SAVE_DIR = r"Main/data/vintrace_reports/disp_reports"
JSON_OUTPUT_PATH = os.path.join(TARGET_SAVE_DIR, "report_index.json")
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
DOWNLOAD_TIMEOUT_MS = 120000

REPORT_CONFIG = {
    "reports_icon_id": "c_170",
    "reports_icon_fallback": "div[title='Reports']",
    "tab_menu_id": "c_382|Text",
    "csv_format_dropdown_id": "c_492",
    "csv_format_option_text": "CSV",
    "composition_checkbox_img_id": "c_419_stateicon",
    "origin_breakdown_dropdown_id": "c_458",
    "second_checkbox_img_id": "c_421_stateicon",
    "extra_checkbox1_img_id": "c_434_stateicon",
    "extra_checkbox2_img_id": "c_435_stateicon",
    "generate_btn_id": "c_414",
    "vintage_dropdown_id": "c_472",
    # input fields for user data mapping
    "date_input_id": "c_460",
    "time_input_id": "c_462",
    "wine_batch_input_id": "c_430"
}

def format_date_time_minus_one(date_time_str):
    """
    Convert '6/1/2023 5:00' to date '06/01/2023' and time '04:59' (24h format, minus one minute)
    """
    import datetime
    date_time_str = date_time_str.strip()
    dt = datetime.datetime.strptime(date_time_str, "%m/%d/%Y %H:%M")
    dt_minus_one = dt - datetime.timedelta(minutes=1)
    date_formatted = dt_minus_one.strftime("%m/%d/%Y")
    time_formatted = dt_minus_one.strftime("%H:%M")
    return date_formatted, time_formatted

def get_root_batch(batch_str):
    # Returns root before slash, e.g., 'CWHRCV22A012/BLK' -> 'CWHRCV22A012'
    return batch_str.split('/')[0] if batch_str else ""

def load_csv_inputs(csv_path, limit_rows=None):
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit_rows and i >= limit_rows:
                break
            # Extract and format date and time (minus one minute)
            date_formatted, time_formatted = format_date_time_minus_one(row['Date'])
            from_bond = row.get('From Bond', '')
            wine_batch_root = get_root_batch(row.get('Wine batch', ''))
            vessel = row.get('Location', '')
            # Add more fields as needed from the CSV (for json output)
            rows.append({
                'date': date_formatted,
                'time': time_formatted,
                'from_bond': from_bond,
                'wine_batch_root': wine_batch_root,
                'vessel': vessel,
                'original_csv': row,  # Store all original fields for linking later
            })
    return rows

def load_existing_json(json_path):
    # Returns a set of filenames already processed
    if not os.path.exists(json_path):
        return set()
    try:
        with open(json_path, "r", encoding="utf-8") as jf:
            data = json.load(jf)
            return set(entry.get("file") for entry in data if "file" in entry)
    except Exception as e:
        print(f"Could not load existing JSON index: {e}")
        return set()

# ... (imports and config unchanged)

async def run():
    load_dotenv()
    USERNAME = os.getenv("VINTRACE_USER")
    PASSWORD = os.getenv("VINTRACE_PW")

    LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
    OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

    report_inputs = load_csv_inputs(CSV_INPUT_PATH, limit_rows=10)
    print(f"Loaded {len(report_inputs)} report parameter sets from CSV.")

    already_processed = load_existing_json(JSON_OUTPUT_PATH)
    print(f"Already processed files: {already_processed}")

    report_json_list = []
    if already_processed:
        with open(JSON_OUTPUT_PATH, "r", encoding="utf-8") as jf:
            report_json_list = json.load(jf)

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

            # Step 4: Click Bulk wine tab
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

            # --- Main Loop: Run for first 5 CSV rows ---
            checkboxes_clicked = False  # <-- add this!
            for idx, params in enumerate(report_inputs):
                file_base = f"vessel_contents_{params['date'].replace('/','-')}_{params['vessel']}_{params['wine_batch_root']}.csv"
                target_path = os.path.join(TARGET_SAVE_DIR, file_base)

                # Skip if already processed
                if file_base in already_processed or os.path.exists(target_path):
                    print(f"Skipping already processed report: {file_base}")
                    continue

                print(f"\n=== Running report {idx+1}/{len(report_inputs)}: {params} ===")

                # Select CSV format (always, because it may reset)
                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["csv_format_dropdown_id"]}', timeout=8000)
                    await page.select_option(f'#{REPORT_CONFIG["csv_format_dropdown_id"]}', label=REPORT_CONFIG["csv_format_option_text"])
                    print("Selected CSV format in dropdown.")
                except Exception as e:
                    print(f"Could not select CSV format: {e}")

                # Only do these before the first actual report run!
                if not checkboxes_clicked:
                    # Click "Composition details" checkbox (first checkbox)
                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["composition_checkbox_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["composition_checkbox_img_id"]}')
                        print("Clicked 'Composition details' checkbox.")
                    except Exception as e:
                        print(f"Could not click 'Composition details' checkbox: {e}")

                    # Select Origin Breakdown dropdown option
                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["origin_breakdown_dropdown_id"]}', timeout=8000)
                        await page.select_option(f'#{REPORT_CONFIG["origin_breakdown_dropdown_id"]}', label="Vintage / Grower / Vineyard / Block / Weigh tag# / Delivery date")
                        print("Selected Origin Breakdown option.")
                    except Exception as e:
                        print(f"Could not select Origin Breakdown option: {e}")

                    # Click second checkbox
                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["second_checkbox_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["second_checkbox_img_id"]}')
                        print("Clicked second checkbox.")
                    except Exception as e:
                        print(f"Could not click second checkbox: {e}")

                    # Click additional checkboxes from user request
                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["extra_checkbox1_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["extra_checkbox1_img_id"]}')
                        print("Clicked extra checkbox #1.")
                    except Exception as e:
                        print(f"Could not click extra checkbox #1: {e}")

                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["extra_checkbox2_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["extra_checkbox2_img_id"]}')
                        print("Clicked extra checkbox #2.")
                    except Exception as e:
                        print(f"Could not click extra checkbox #2: {e}")

                    # Select Vintage year (if needed, only on first run)
                    # try:
                    #     await page.wait_for_selector(f'#{REPORT_CONFIG["vintage_dropdown_id"]}', timeout=8000)
                    #     await page.click(f'#{REPORT_CONFIG["vintage_dropdown_id"]}')
                    #     result = await page.select_option(f'#{REPORT_CONFIG["vintage_dropdown_id"]}', label='2025')
                    #     print(f"Vintage select result: {result}")
                    # except Exception as e:
                    #     print(f"Could not select vintage dropdown option: {e}")

                    checkboxes_clicked = True  # <-- set after clicking!

                # Fill Date Field
                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["date_input_id"]}', timeout=8000)
                    await page.fill(f'#{REPORT_CONFIG["date_input_id"]}', params['date'])
                    print(f"Filled date field with: {params['date']}")
                except Exception as e:
                    print(f"Could not fill date field: {e}")

                # Fill Time Field (now 1 minute before CSV value)
                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["time_input_id"]}', timeout=8000)
                    await page.fill(f'#{REPORT_CONFIG["time_input_id"]}', params['time'])
                    print(f"Filled time field with: {params['time']}")
                except Exception as e:
                    print(f"Could not fill time field: {e}")

                # Fill Wine Batch Field
                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["wine_batch_input_id"]}', timeout=8000)
                    await page.fill(f'#{REPORT_CONFIG["wine_batch_input_id"]}', params['wine_batch_root'])
                    print(f"Filled wine batch field with: {params['wine_batch_root']}")
                except Exception as e:
                    print(f"Could not fill wine batch field: {e}")

                # Pause for 1 second before clicking Generate (to let fields update)
                await page.wait_for_timeout(1000)

                # Click Generate button and download report
                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["generate_btn_id"]}', timeout=8000)
                    async with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
                        await page.click(f'#{REPORT_CONFIG["generate_btn_id"]}')
                        print("Clicked 'Generate...' button.")
                    download = await download_info.value
                    temp_path = await download.path()
                    # Save with unique file name using vessel and wine batch root and date
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    shutil.copy(temp_path, target_path)
                    print(f"Copied downloaded report to: {target_path}")
                    os.remove(temp_path)

                    # Add to report_json_list for output
                    json_entry = {
                        "file": file_base,
                        "date": params['date'],
                        "time": params['time'],
                        "from_bond": params['from_bond'],
                        "wine_batch_root": params['wine_batch_root'],
                        "vessel": params['vessel'],
                        # You can add more CSV values here
                        "original_csv": params['original_csv']
                    }
                    report_json_list.append(json_entry)

                except Exception as e:
                    print(f"Could not click the Generate button or download file: {e}")

                await page.wait_for_timeout(1500)  # Wait before next report

            print("\nAll reports completed. The browser will remain open for inspection and manual action.\n")
            await page.pause()

    finally:
        # Write JSON output for linking/process later
        with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as jf:
            json.dump(report_json_list, jf, indent=2)
        print(f"JSON index written to {JSON_OUTPUT_PATH}")
        print(f"All unique reports have been saved in: {TARGET_SAVE_DIR}")

if __name__ == "__main__":
    asyncio.run(run())