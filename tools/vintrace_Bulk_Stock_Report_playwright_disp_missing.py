#  python tools/vintrace_Bulk_Stock_Report_playwright_disp_missing.py


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
ZERO_RECORDS_PATH = os.path.join(TARGET_SAVE_DIR, "zero_records_info.json")
DEBUG_INPUTS_PATH = os.path.join(TARGET_SAVE_DIR, "debug_inputs.json")
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
DOWNLOAD_TIMEOUT_MS = 1200000

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
    "date_input_id": "c_460",
    "time_input_id": "c_462",
    "wine_batch_input_id": "c_430"
}

def format_date_time_minus_one(date_time_str):
    import datetime
    date_time_str = date_time_str.strip()
    dt = datetime.datetime.strptime(date_time_str, "%m/%d/%Y %H:%M")
    dt_minus_one = dt - datetime.timedelta(minutes=1)
    date_formatted = dt_minus_one.strftime("%m/%d/%Y")
    time_formatted = dt_minus_one.strftime("%H:%M")
    return date_formatted, time_formatted

def get_root_batch(batch_str):
    return batch_str.split('/')[0] if batch_str else ""

def load_csv_inputs(csv_path):
    inputs = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_raw = row.get('Date', '').strip()
            if not date_raw:
                # Skip this row, log if needed
                print(f"Skipping row due to missing date: {row}")
                continue
            try:
                date_formatted, time_formatted = format_date_time_minus_one(date_raw)
            except Exception as ex:
                print(f"Skipping row due to invalid date '{date_raw}': {ex}")
                continue
            from_bond = row.get('From Bond', '')
            wine_batch_root = get_root_batch(row.get('Wine batch', ''))
            vessel = row.get('Location', '')
            file_base = f"vessel_contents_{date_formatted.replace('/','-')}_{vessel}_{wine_batch_root}.csv"
            inputs[file_base] = {
                'date': date_formatted,
                'time': time_formatted,
                'from_bond': from_bond,
                'wine_batch_root': wine_batch_root,
                'vessel': vessel,
                'original_csv': row,
            }
    return inputs

def load_zero_records(zero_records_path):
    # Loads the zero_records_info.json entries as a list of dicts
    if not os.path.exists(zero_records_path):
        return []
    try:
        with open(zero_records_path, "r", encoding="utf-8") as zr:
            return json.load(zr)
    except Exception as e:
        print(f"Could not load zero_records_info.json: {e}")
        return []

async def run():
    load_dotenv()
    USERNAME = os.getenv("VINTRACE_USER")
    PASSWORD = os.getenv("VINTRACE_PW")

    LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
    OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

    csv_inputs = load_csv_inputs(CSV_INPUT_PATH)
    zero_records = load_zero_records(ZERO_RECORDS_PATH)
    print(f"Loaded {len(zero_records)} zero-record entries to process.")

    # For output
    report_json_list = []
    debug_inputs_list = []

    # Optionally load previous report index (if you want to add to it)
    if os.path.exists(JSON_OUTPUT_PATH):
        try:
            with open(JSON_OUTPUT_PATH, "r", encoding="utf-8") as jf:
                report_json_list = json.load(jf)
        except Exception as e:
            print(f"Could not load report_index.json: {e}")

    # Optionally load previous debug file
    if os.path.exists(DEBUG_INPUTS_PATH):
        try:
            with open(DEBUG_INPUTS_PATH, "r", encoding="utf-8") as df:
                debug_inputs_list = json.load(df)
        except Exception as e:
            print(f"Could not load debug_inputs.json: {e}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()

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

            await page.goto(OLD_URL)
            print("Navigated to OLD_URL.")
            await page.wait_for_timeout(2000)

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

            checkboxes_clicked = False
            for idx, record in enumerate(zero_records):
                file_base = record.get("file")
                target_path = os.path.join(TARGET_SAVE_DIR, file_base)

                # Look up CSV row by file_base
                params = csv_inputs.get(file_base)
                if not params:
                    print(f"CSV input row not found for zero-record file: {file_base}")
                    debug_entry = {
                        "file": file_base,
                        "status": "skipped",
                        "error": "CSV input row not found for this zero-record file.",
                        "reason": record.get("reason"),
                        "vessel": record.get("vessel"),
                        "batchcode": record.get("batchcode"),
                    }
                    debug_inputs_list.append(debug_entry)
                    continue

                print(f"\n=== Running zero-record report {idx+1}/{len(zero_records)}: {file_base} ===")

                debug_entry = {
                    "file": file_base,
                    "date": params['date'],
                    "time": params['time'],
                    "wine_batch_root": params['wine_batch_root'],
                    "vessel": params['vessel'],
                    "from_bond": params['from_bond'],
                    "original_csv": params['original_csv'],
                    "status": "attempted",
                    "error": None,
                    "reason": record.get("reason"),
                }

                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["csv_format_dropdown_id"]}', timeout=8000)
                    await page.select_option(f'#{REPORT_CONFIG["csv_format_dropdown_id"]}', label=REPORT_CONFIG["csv_format_option_text"])
                    print("Selected CSV format in dropdown.")
                except Exception as e:
                    debug_entry["status"] = "failed"
                    debug_entry["error"] = f"Could not select CSV format: {e}"

                if not checkboxes_clicked:
                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["composition_checkbox_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["composition_checkbox_img_id"]}')
                        print("Clicked 'Composition details' checkbox.")
                    except Exception as e:
                        debug_entry["status"] = "failed"
                        debug_entry["error"] = f"Could not click 'Composition details' checkbox: {e}"

                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["origin_breakdown_dropdown_id"]}', timeout=8000)
                        await page.select_option(f'#{REPORT_CONFIG["origin_breakdown_dropdown_id"]}', label="Vintage / Grower / Vineyard / Block / Weigh tag# / Delivery date")
                        print("Selected Origin Breakdown option.")
                    except Exception as e:
                        debug_entry["status"] = "failed"
                        debug_entry["error"] = f"Could not select Origin Breakdown option: {e}"

                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["second_checkbox_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["second_checkbox_img_id"]}')
                        print("Clicked second checkbox.")
                    except Exception as e:
                        debug_entry["status"] = "failed"
                        debug_entry["error"] = f"Could not click second checkbox: {e}"

                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["extra_checkbox1_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["extra_checkbox1_img_id"]}')
                        print("Clicked extra checkbox #1.")
                    except Exception as e:
                        debug_entry["status"] = "failed"
                        debug_entry["error"] = f"Could not click extra checkbox #1: {e}"

                    try:
                        await page.wait_for_selector(f'#{REPORT_CONFIG["extra_checkbox2_img_id"]}', timeout=8000)
                        await page.click(f'#{REPORT_CONFIG["extra_checkbox2_img_id"]}')
                        print("Clicked extra checkbox #2.")
                    except Exception as e:
                        debug_entry["status"] = "failed"
                        debug_entry["error"] = f"Could not click extra checkbox #2: {e}"

                    checkboxes_clicked = True

                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["date_input_id"]}', timeout=8000)
                    await page.fill(f'#{REPORT_CONFIG["date_input_id"]}', params['date'])
                    print(f"Filled date field with: {params['date']}")
                except Exception as e:
                    debug_entry["status"] = "failed"
                    debug_entry["error"] = f"Could not fill date field: {e}"

                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["time_input_id"]}', timeout=8000)
                    await page.fill(f'#{REPORT_CONFIG["time_input_id"]}', params['time'])
                    print(f"Filled time field with: {params['time']}")
                except Exception as e:
                    debug_entry["status"] = "failed"
                    debug_entry["error"] = f"Could not fill time field: {e}"

                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["wine_batch_input_id"]}', timeout=8000)
                    await page.fill(f'#{REPORT_CONFIG["wine_batch_input_id"]}', params['wine_batch_root'])
                    print(f"Filled wine batch field with: {params['wine_batch_root']}")
                except Exception as e:
                    debug_entry["status"] = "failed"
                    debug_entry["error"] = f"Could not fill wine batch field: {e}"

                await page.wait_for_timeout(1000)

                try:
                    await page.wait_for_selector(f'#{REPORT_CONFIG["generate_btn_id"]}', timeout=8000)
                    async with page.expect_download(timeout=DOWNLOAD_TIMEOUT_MS) as download_info:
                        await page.click(f'#{REPORT_CONFIG["generate_btn_id"]}')
                        print("Clicked 'Generate...' button.")
                    download = await download_info.value
                    temp_path = await download.path()
                    # Always overwrite the file
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    shutil.copy(temp_path, target_path)
                    print(f"Copied downloaded report to: {target_path}")
                    os.remove(temp_path)

                    json_entry = {
                        "file": file_base,
                        "date": params['date'],
                        "time": params['time'],
                        "from_bond": params['from_bond'],
                        "wine_batch_root": params['wine_batch_root'],
                        "vessel": params['vessel'],
                        "original_csv": params['original_csv']
                    }
                    report_json_list.append(json_entry)
                    debug_entry["status"] = "success"
                except Exception as e:
                    debug_entry["status"] = "failed"
                    debug_entry["error"] = f"Could not click the Generate button or download file: {e}"

                debug_inputs_list.append(debug_entry)
                await page.wait_for_timeout(1500)

            print("\nAll zero-record reports attempted. The browser will remain open for inspection and manual action.\n")
            await page.pause()

    finally:
        with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as jf:
            json.dump(report_json_list, jf, indent=2)
        print(f"JSON index written to {JSON_OUTPUT_PATH}")
        print(f"All unique reports have been saved in: {TARGET_SAVE_DIR}")

        with open(DEBUG_INPUTS_PATH, "w", encoding="utf-8") as df:
            json.dump(debug_inputs_list, df, indent=2)
        print(f"Debug inputs written to {DEBUG_INPUTS_PATH}")

if __name__ == "__main__":
    asyncio.run(run())