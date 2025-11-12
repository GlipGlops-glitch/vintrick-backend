#  python tools/vintrace_Grape_Report_with_bookingSummary.py


import os
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# Helper function to robustly click checkboxes
def safe_click_checkbox(driver, wait, checkbox_id, description):
    try:
        checkbox = wait.until(EC.presence_of_element_located((By.ID, checkbox_id)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        wait.until(EC.visibility_of_element_located((By.ID, checkbox_id)))
        wait.until(EC.element_to_be_clickable((By.ID, checkbox_id)))
        # Try normal click
        try:
            checkbox.click()
        except Exception:
            # Fallback to JS click
            driver.execute_script("arguments[0].click();", checkbox)
        print(f"Clicked the {description} ({checkbox_id}).")
    except Exception as e:
        print(f"Could not click the {description} ({checkbox_id}): {e}")

# Load credentials from .env
load_dotenv()
USERNAME = os.getenv("VINTRACE_USER")
PASSWORD = os.getenv("VINTRACE_PW")

LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

REPORT_FILENAME = "grape_detailz.csv"
TARGET_SAVE_DIR = r"Main/data/vintrace_reports/"
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
TARGET_FILE_PATH = os.path.join(TARGET_SAVE_DIR, REPORT_FILENAME)

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": TARGET_SAVE_DIR,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 60)  # Increased timeout for slow pages

try:
    # Step 1: Go to login page
    driver.get(LOGIN_URL)

    # Step 2: Log in using HTML fields provided
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    time.sleep(3)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]"))).click()
    time.sleep(3)
    # Step 3: Wait for login to complete
    wait.until(EC.url_changes(LOGIN_URL))

    # Step 4: Navigate to OLD_URL (the old Vintrace UI)
    driver.get(OLD_URL)
    print("Navigated to OLD_URL.")
    time.sleep(3)  # Optional: wait for page rendering after navigation

    # Step 5: Click on Reports quick launch icon by ID or title
    try:
        reports_icon = wait.until(EC.element_to_be_clickable((By.ID, "c_170")))
        reports_icon.click()
        print("Clicked the 'Reports' quick launch icon by ID.")
    except Exception as e:
        print(f"Could not click Reports icon by ID: {e}")
        # Fallback: Try by title
        try:
            reports_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@title='Reports']")))
            reports_icon.click()
            print("Clicked the 'Reports' quick launch icon by title.")
        except Exception as e2:
            print(f"Could not click Reports icon by title: {e2}")

    time.sleep(2)  # Optional: wait for menu to expand

    # Step 6: Click on Vintage/Harvest tab/menu
    try:
        vintage = wait.until(EC.element_to_be_clickable((By.ID, "c_384|Text")))
        vintage.click()
        print("Clicked 'Vintage/Harvest' by ID.")
    except Exception as e:
        print(f"Could not click Vintage/Harvest by ID: {e}")
        # Fallback: Try by visible text
        try:
            time.sleep(2)
            vintage = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Vintage/Harvest']")))
            vintage.click()
            print("Clicked 'Vintage/Harvest' by text.")
        except Exception as e2:
            print(f"Could not click Vintage/Harvest by text: {e2}")
            # Fallback: Try clicking parent if span is not clickable
            try:
                time.sleep(2)
                vintage_span = wait.until(EC.presence_of_element_located((By.ID, "c_384|Text")))
                parent = vintage_span.find_element(By.XPATH, "..")
                wait.until(EC.element_to_be_clickable(parent)).click()
                print("Clicked parent of 'Vintage/Harvest' span.")
            except Exception as e3:
                print(f"Could not click parent of Vintage/Harvest span: {e3}")

    # Step 7: Select "CSV" from the dropdown inside the table cell
    try:
        time.sleep(2)
        cell = wait.until(EC.presence_of_element_located((By.ID, "c_552_cell_c_600")))
        select_element = cell.find_element(By.ID, "c_600")
        select_obj = Select(select_element)
        select_obj.select_by_visible_text("CSV")
        print("Selected 'CSV' from the table dropdown.")
    except Exception as e:
        print(f"Could not select 'CSV' from table dropdown: {e}")

    # Step 8: Select "2025" from the vintage dropdown inside its cell
    try:
            # Step 9: Robustly click the NEW checkboxes (c_556_stateicon and c_962_stateicon)
        time.sleep(2)
        safe_click_checkbox(driver, wait, "c_556_stateicon", "first checkbox (c_556_stateicon)")
        safe_click_checkbox(driver, wait, "c_962_stateicon", "second checkbox (c_962_stateicon)")

        time.sleep(2)
        cell_vintage = wait.until(EC.presence_of_element_located((By.ID, "c_566_td_c_567")))
        select_vintage = cell_vintage.find_element(By.ID, "c_567")
        select_obj_vintage = Select(select_vintage)
        select_obj_vintage.select_by_visible_text("2025")
        print("Selected '2025' from the vintage dropdown.")
    except Exception as e:
        print(f"Could not select '2025' from vintage dropdown: {e}")

    # Step 10: Click the "Generate..." button to run the report
    try:
        time.sleep(2)
        generate_btn = wait.until(EC.element_to_be_clickable((By.ID, "c_517")))
        generate_btn.click()
        print("Clicked the 'Generate...' button to run the report.")
    except Exception as e:
        print(f"Could not click the Generate button: {e}")

    print("Report generation triggered. Waiting for download to complete...")
    download_wait_time = 15
    time.sleep(download_wait_time)  # Wait for file to download (adjust as needed)

    # Step 11: Find the latest downloaded file with the VINx2_DeliveryReport_2025* pattern and rename/replace grape_detail.csv
    try:
        # Find CSV files that start with "VINx2_DeliveryReport_2025"
        csv_files = [f for f in os.listdir(TARGET_SAVE_DIR)
                     if f.startswith("VINx2_DeliveryReport_2025") and f.lower().endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("No VINx2_DeliveryReport_2025*.csv file found after report download.")

        # Get the most recently modified matching file
        csv_files_fullpath = [os.path.join(TARGET_SAVE_DIR, f) for f in csv_files]
        latest_file = max(csv_files_fullpath, key=os.path.getmtime)

        # If the target file already exists in target dir, remove it first
        if os.path.exists(TARGET_FILE_PATH):
            os.remove(TARGET_FILE_PATH)

        shutil.move(latest_file, TARGET_FILE_PATH)
        print(f"Renamed and moved downloaded report to: {TARGET_FILE_PATH}")
    except Exception as e:
        print(f"Error moving/renaming downloaded report: {e}")

finally:
    driver.quit()

print(f"Report should be downloaded and named: {os.path.join(TARGET_SAVE_DIR, REPORT_FILENAME)}")