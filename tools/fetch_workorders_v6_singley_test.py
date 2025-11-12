# python tools/fetch_workorders_v6_singley_test.py

import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")
VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
WO_IDS_PATH = "Main/data/GET--work_orders_paged/extraction_job_ids.json"  # adjust path as needed

headers = {
    "Authorization": f"Bearer {VINTRACE_API_TOKEN}",
    "Accept": "application/json"
}

# Load work order IDs from wo_ids.json
try:
    with open(WO_IDS_PATH, "r", encoding="utf-8") as f:
        wo_ids = json.load(f)
except Exception as e:
    print(f"Failed to load wo_ids.json: {e}")
    wo_ids = []

print(f"Loaded {len(wo_ids)} work order IDs.")

# Output directory for details
output_dir = "Main/data/GET--work_orders_paged/v6_details_jobs"
os.makedirs(output_dir, exist_ok=True)

delay_sec = 0.5  # delay between requests


url = f"{BASE_URL}/smwe/api/v6/extraction/start?taskId=183585"
try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code} | job_id: test| URL: {url}")
    detail_path = os.path.join(output_dir, f"test.json")
    if response.status_code == 200:
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)
    else:
        # Save error info for troubleshooting
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump({"error": response.text, "status_code": response.status_code}, f, indent=2, ensure_ascii=False)
except Exception as e:
    print(f"Exception for job_id test: {e}")
time.sleep(delay_sec)