# python tools/webdriver_agcode_harvestloads.py


import os
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv

# Load credentials from .env
load_dotenv()
USERNAME = os.getenv("AGCODE_UN")  # Make sure .env variable matches!
PASSWORD = os.getenv("AGCODE_PW")

LOGIN_URL = "https://www.agcode.net/AgCodeNET2/secure/login.aspx"
REPORT_URL = "https://www.agcode.net/AgCodeNET2/secure/BIPortal/NewBIPortal.aspx?PID=17&PCID=88"

TEMP_DOWNLOAD_DIR = r"C:\Users\cah01\Code\AgCode\AgCode\temp_download"
os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)

TARGET_HTML_PATH = os.path.join(TEMP_DOWNLOAD_DIR, "harvest_loads.html")
TARGET_CSV_PATH = os.path.join(TEMP_DOWNLOAD_DIR, "harvest_loads.csv")

def html_table_to_csv(html_path, csv_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table")
    if not table:
        print("No table found in HTML!")
        return

    thead = table.find("thead")
    headers = []
    if thead:
        header_row = thead.find("tr")
        headers = [th.text.strip() for th in header_row.find_all("th")]

    tbody = table.find("tbody")
    rows = []
    for tr in tbody.find_all("tr"):
        row = []
        for td in tr.find_all("td"):
            cell = td.text.strip()
            if cell == "\xa0" or cell == "&nbsp;":
                cell = ""
            row.append(cell)
        rows.append(row)

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)

    print(f"Converted HTML table to CSV: {csv_path}")

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

    # Step 2: Log in
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

    print("Waiting for HTML to render and be ready to save...")
    time.sleep(10)  # Wait for the table to render

    # Step 5: Save the HTML page source
    try:
        page_source = driver.page_source
        with open(TARGET_HTML_PATH, "w", encoding="utf-8") as file:
            file.write(page_source)
        print(f"Saved HTML page source to {TARGET_HTML_PATH}")
    except Exception as e:
        print(f"Error saving HTML source: {e}")

    # Step 6: Convert HTML table to CSV
    try:
        html_table_to_csv(TARGET_HTML_PATH, TARGET_CSV_PATH)
    except Exception as e:
        print(f"Error converting HTML to CSV: {e}")

finally:
    driver.quit()

print(f"Report should be downloaded, saved as HTML at: {TARGET_HTML_PATH}, and converted to CSV at: {TARGET_CSV_PATH}")