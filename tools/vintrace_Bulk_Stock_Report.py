#  python tools/vintrace_Bulk_Stock_Report.py



import os
import shutil
import csv
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from inputs_scraper import inputs_scraper

# ------- EASY REPORT CONFIG SECTION -------
def get_todays_date_str():
    """Returns today's date as a string in YYYY-MM-DD format."""
    return datetime.datetime.now().strftime("%Y-%m-%d")

REPORT_CONFIG = {
    "report_filename": f"vessel_contents_{get_todays_date_str()}.csv",
    "download_pattern": "VINx2_DeliveryReport_2025",
    "reports_icon": {
        "by": By.ID,
        "value": "c_170",
        "fallback_by": By.XPATH,
        "fallback_value": "//div[@title='Reports']"
    },
    "tab_menu": {
        "by": By.ID,
        "value": "c_382|Text",
        "fallback_by": By.XPATH,
        "fallback_value": "//span[text()='Bulk wine']"
    },
    "format_dropdown": {
        "dropdown_id": "c_492",       # Updated from latest HTML
        "option_text": "CSV"
    },
    "year_dropdown": {
        "dropdown_id": "c_1047",
        "option_text": "2025"
    },
    "composition_checkbox_img_id": "c_419_stateicon",  # <img> for checkbox
    "origin_breakdown_dropdown_id": "c_458",
    "origin_breakdown_option_text": "Vintage / Grower / Vineyard / Block / Weigh tag# / Delivery date",
    "breakdown_comp_checkbox_img_id": "c_421_stateicon",  # <img> for second checkbox
    "generate_btn": {
        "by": By.ID,
        "value": "c_3693"
    }
}
# ------------------------------------------

# ---- CSV Integration Section ----
CSV_PATH = "Main/data/dispatch_inputs.csv"  # Update path as needed

def load_and_transform_csv(csv_path):
    processed_rows = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Split date and time
            date_time_str = row.get("Date", "").strip()
            if not date_time_str:
                continue
            try:
                # Try with 24-hour first, then fallback to 12-hour
                dt = datetime.datetime.strptime(date_time_str, "%m/%d/%Y %H:%M")
            except ValueError:
                try:
                    dt = datetime.datetime.strptime(date_time_str, "%m/%d/%Y %I:%M")
                except Exception as e:
                    print(f"Could not parse date: {date_time_str} ({e})")
                    continue

            short_date = dt.strftime("%m/%d/%Y")
            time_24hr = dt.strftime("%H:%M")

            from_bond = row.get("From Bond", "").strip()
            winery = row.get("Winery", "").strip()
            vessel = row.get("Location", "").strip()

            processed_rows.append({
                "short_date": short_date,
                "time_24hr": time_24hr,
                "from_bond": from_bond,
                "winery": winery,
                "vessel": vessel,
            })
    return processed_rows
# ------------------------------------------

# Load credentials from .env
load_dotenv()
USERNAME = os.getenv("VINTRACE_USER")
PASSWORD = os.getenv("VINTRACE_PW")

LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

TARGET_SAVE_DIR = r"Main/data/vintrace_reports/"
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
TARGET_FILE_PATH = os.path.join(TARGET_SAVE_DIR, REPORT_CONFIG["report_filename"])

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": TARGET_SAVE_DIR,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 60)

try:
    # Step 1: Go to login page
    driver.get(LOGIN_URL)
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    time.sleep(3)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]"))).click()
    time.sleep(3)
    wait.until(EC.url_changes(LOGIN_URL))

    # Step 2: Navigate to OLD_URL
    driver.get(OLD_URL)
    print("Navigated to OLD_URL.")
    time.sleep(3)

    # Step 3: Click reports icon
    try:
        reports_icon = wait.until(EC.element_to_be_clickable((REPORT_CONFIG["reports_icon"]["by"], REPORT_CONFIG["reports_icon"]["value"])))
        reports_icon.click()
        print("Clicked the 'Reports' quick launch icon.")
    except Exception as e:
        print(f"Could not click Reports icon: {e}")
        try:
            reports_icon = wait.until(EC.element_to_be_clickable((REPORT_CONFIG["reports_icon"]["fallback_by"], REPORT_CONFIG["reports_icon"]["fallback_value"])))
            reports_icon.click()
            print("Clicked the 'Reports' quick launch icon (fallback).")
        except Exception as e2:
            print(f"Could not click Reports icon (fallback): {e2}")

    time.sleep(2)

    # Step 4: Click tab/menu for report type
    try:
        tab = wait.until(EC.element_to_be_clickable((REPORT_CONFIG["tab_menu"]["by"], REPORT_CONFIG["tab_menu"]["value"])))
        tab.click()
        print("Clicked report tab/menu.")
    except Exception as e:
        print(f"Could not click tab/menu: {e}")
        try:
            tab = wait.until(EC.element_to_be_clickable((REPORT_CONFIG["tab_menu"]["fallback_by"], REPORT_CONFIG["tab_menu"]["fallback_value"])))
            tab.click()
            print("Clicked report tab/menu (fallback).")
        except Exception as e2:
            print(f"Could not click tab/menu (fallback): {e2}")

    # Scrape inputs
    inputs_scraper(driver, section_name="Bulk wine", output_dir=TARGET_SAVE_DIR)

    # Step 5: Select "CSV" format
    try:
        select_element = wait.until(EC.presence_of_element_located((By.ID, REPORT_CONFIG["format_dropdown"]["dropdown_id"])))
        select_obj = Select(select_element)
        select_obj.select_by_visible_text(REPORT_CONFIG["format_dropdown"]["option_text"])
        print("Selected format CSV in dropdown.")
    except Exception as e:
        print(f"Could not select CSV format: {e}")

    # Step 6: Select year 2025
    try:
        year_dropdown = wait.until(EC.presence_of_element_located((By.ID, REPORT_CONFIG["year_dropdown"]["dropdown_id"])))
        select_year = Select(year_dropdown)
        select_year.select_by_visible_text(REPORT_CONFIG["year_dropdown"]["option_text"])
        print("Selected year 2025 in dropdown.")
    except Exception as e:
        print(f"Could not select year: {e}")

    # Step 7: Click "Composition details" checkbox (via <img>)
    try:
        comp_checkbox_img = wait.until(EC.presence_of_element_located((By.ID, REPORT_CONFIG["composition_checkbox_img_id"])))
        driver.execute_script("arguments[0].scrollIntoView(true);", comp_checkbox_img)
        comp_checkbox_img.click()
        print("Clicked 'Composition details' checkbox.")
    except Exception as e:
        print(f"Could not click 'Composition details' checkbox: {e}")

    # Step 8: Select Origin Breakdown dropdown option
    try:
        origin_dropdown = wait.until(EC.presence_of_element_located((By.ID, REPORT_CONFIG["origin_breakdown_dropdown_id"])))
        select_origin = Select(origin_dropdown)
        select_origin.select_by_visible_text(REPORT_CONFIG["origin_breakdown_option_text"])
        print(f"Selected Origin Breakdown option: {REPORT_CONFIG['origin_breakdown_option_text']}")
    except Exception as e:
        print(f"Could not select Origin Breakdown option: {e}")

    # Step 9: Click "Breakdown comp. (CSV)" checkbox (via <img>)
    try:
        breakdown_checkbox_img = wait.until(EC.presence_of_element_located((By.ID, REPORT_CONFIG["breakdown_comp_checkbox_img_id"])))
        driver.execute_script("arguments[0].scrollIntoView(true);", breakdown_checkbox_img)
        breakdown_checkbox_img.click()
        print("Clicked 'Breakdown comp. (CSV)' checkbox.")
    except Exception as e:
        print(f"Could not click 'Breakdown comp. (CSV)' checkbox: {e}")

    # ---- New Step: Fill fields from CSV for each row ----
    csv_data = load_and_transform_csv(CSV_PATH)
    for idx, item in enumerate(csv_data):
        print(f"Processing CSV row #{idx+1}: {item}")

        # NOTE: REPLACE the field IDs below with the actual IDs/XPaths from your webpage!
        try:
            # Fill Date field
            date_field = wait.until(EC.presence_of_element_located((By.ID, "date_field_id")))  # <-- Replace
            date_field.clear()
            date_field.send_keys(item["short_date"])
            print(f"Filled 'Date' with: {item['short_date']}")
        except Exception as e:
            print(f"Could not fill 'Date' field: {e}")

        try:
            # Fill Time field
            time_field = wait.until(EC.presence_of_element_located((By.ID, "time_field_id")))  # <-- Replace
            time_field.clear()
            time_field.send_keys(item["time_24hr"])
            print(f"Filled 'Time' with: {item['time_24hr']}")
        except Exception as e:
            print(f"Could not fill 'Time' field: {e}")

        try:
            # Fill From Bond field
            from_bond_field = wait.until(EC.presence_of_element_located((By.ID, "from_bond_field_id")))  # <-- Replace
            from_bond_field.clear()
            from_bond_field.send_keys(item["from_bond"])
            print(f"Filled 'From Bond' with: {item['from_bond']}")
        except Exception as e:
            print(f"Could not fill 'From Bond' field: {e}")

        try:
            # Fill Winery field
            winery_field = wait.until(EC.presence_of_element_located((By.ID, "winery_field_id")))  # <-- Replace
            winery_field.clear()
            winery_field.send_keys(item["winery"])
            print(f"Filled 'Winery' with: {item['winery']}")
        except Exception as e:
            print(f"Could not fill 'Winery' field: {e}")

        try:
            # Fill Vessel (Location) field
            vessel_field = wait.until(EC.presence_of_element_located((By.ID, "vessel_field_id")))  # <-- Replace
            vessel_field.clear()
            vessel_field.send_keys(item["vessel"])
            print(f"Filled 'Vessel' (Location) with: {item['vessel']}")
        except Exception as e:
            print(f"Could not fill 'Vessel' (Location) field: {e}")

        # Step 10: Click generate button for this row
        try:
            generate_btn = wait.until(EC.element_to_be_clickable((REPORT_CONFIG["generate_btn"]["by"], REPORT_CONFIG["generate_btn"]["value"])))
            generate_btn.click()
            print("Clicked the 'Generate...' button to run the report for this CSV row.")
        except Exception as e:
            print(f"Could not click the Generate button: {e}")

        print("Report generation triggered. Waiting for download to complete...")
        time.sleep(15)

        # Step 11: Find and rename latest downloaded file for each CSV row
        try:
            csv_files = [f for f in os.listdir(TARGET_SAVE_DIR)
                         if f.startswith(REPORT_CONFIG["download_pattern"]) and f.lower().endswith('.csv')]
            if not csv_files:
                raise FileNotFoundError(f"No {REPORT_CONFIG['download_pattern']}*.csv file found after report download.")

            csv_files_fullpath = [os.path.join(TARGET_SAVE_DIR, f) for f in csv_files]
            latest_file = max(csv_files_fullpath, key=os.path.getmtime)

            # Name file by row number to avoid overwrite
            target_file_path = os.path.join(TARGET_SAVE_DIR, f"{REPORT_CONFIG['report_filename'].replace('.csv', f'_{idx+1}.csv')}")
            if os.path.exists(target_file_path):
                os.remove(target_file_path)
            shutil.move(latest_file, target_file_path)
            print(f"Renamed and moved downloaded report to: {target_file_path}")
        except Exception as e:
            print(f"Error moving/renaming downloaded report: {e}")

finally:
    driver.quit()

print(f"All reports from CSV should be downloaded and named sequentially in: {TARGET_SAVE_DIR}")