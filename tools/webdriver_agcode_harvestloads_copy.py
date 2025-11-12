# python tools/webdriver_agcode_harvestloads_copy.py


import os
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Load credentials from .env
load_dotenv()
USERNAME = os.getenv("AGCODE_UN")  # Make sure .env variable matches!
PASSWORD = os.getenv("AGCODE_PW")

LOGIN_URL = "https://www.agcode.net/AgCodeNET2/secure/login.aspx"
REPORT_URL = "https://www.agcode.net/AgCodeNET2/secure/BIPortal/NewBIPortal.aspx?PID=17&PCID=88"

TEMP_DOWNLOAD_DIR = r"C:\Users\cah01\Code\AgCode\AgCode\temp_download"
os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)

TARGET_FILE_PATH = os.path.join(TEMP_DOWNLOAD_DIR, "harvest_loads.csv")

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": TEMP_DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

try:
    # Step 1: Go to login page
    driver.get(LOGIN_URL)
    print("Opened login page.")

    time.sleep(2)  # Let page render

    # Debug: Print all input fields found
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print("Found input fields:")
    for inp in inputs:
        print(f"input: id={inp.get_attribute('id')} name={inp.get_attribute('name')} type={inp.get_attribute('type')}")

    # Step 2: Log in using HTML fields provided
    try:
        username_field = wait.until(EC.presence_of_element_located((By.ID, "txtUsername")))
        print("Found username field.")
        username_field.clear()
        username_field.send_keys(USERNAME)
    except Exception as e:
        print(f"Could not find/fill username field: {e}")

    try:
        password_field = wait.until(EC.presence_of_element_located((By.ID, "txtPassword")))
        print("Found password field.")
        password_field.clear()
        password_field.send_keys(PASSWORD)
    except Exception as e:
        print(f"Could not find/fill password field: {e}")

    time.sleep(2)
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnLogin")))
        print("Found login button.")
        login_btn.click()
    except Exception as e:
        print(f"Could not find/click login button: {e}")

    time.sleep(5)  # Wait for redirect
    print(f"Current URL after login: {driver.current_url}")

    # Step 3: Navigate to REPORT_URL
    driver.get(REPORT_URL)
    print("Navigated to REPORT_URL.")
    time.sleep(4)  # Wait for page rendering

    # Step 4: Click the "Extract" button via its ID
    try:
        extract_btn = wait.until(EC.element_to_be_clickable((By.ID, "exportDataControl")))
        extract_btn.click()
        print("Clicked the 'Extract' button to export the report.")
    except Exception as e:
        print(f"Could not click 'Extract' button: {e}")

    print("Report extraction triggered. Waiting for download to complete...")
    download_wait_time = 20
    time.sleep(download_wait_time)

    # Step 5: Remove any previous harvest_loads.csv before saving new
    try:
        if os.path.exists(TARGET_FILE_PATH):
            os.remove(TARGET_FILE_PATH)

        # Find .xls files starting with "Harvest-Loads_All"
        xls_files = [f for f in os.listdir(TEMP_DOWNLOAD_DIR)
                      if f.startswith("Harvest-Loads_All") and f.lower().endswith('.xls')]
        if not xls_files:
            raise FileNotFoundError("No Harvest-Loads_All*.xls file found after report download.")

        xls_files_fullpath = [os.path.join(TEMP_DOWNLOAD_DIR, f) for f in xls_files]
        latest_file = max(xls_files_fullpath, key=os.path.getmtime)

        # Move the latest .xls file to a canonical name (harvest_loads.xls) BEFORE conversion
        harvest_loads_xls = os.path.join(TEMP_DOWNLOAD_DIR, "harvest_loads.xls")
        shutil.move(latest_file, harvest_loads_xls)
        print(f"Moved {latest_file} to {harvest_loads_xls}")

        # Convert Excel to CSV using pandas
        df = pd.read_excel(harvest_loads_xls, engine='xlrd')
        df.to_csv(TARGET_FILE_PATH, index=False)
        print(f"Converted and saved downloaded report to: {TARGET_FILE_PATH}")

        # Remove the .xls file after conversion
        os.remove(harvest_loads_xls)

        # Remove any other Harvest-Loads_All*.xls files left
        for f in xls_files_fullpath:
            if os.path.exists(f):
                os.remove(f)

    except Exception as e:
        print(f"Error converting/moving downloaded report: {e}")

finally:
    driver.quit()

print(f"Report should be downloaded and saved as CSV at: {TARGET_FILE_PATH}")