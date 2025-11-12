#python tools/job_GET_copy.py
import http.client
import json
import os

# Set up connection and authentication
conn = http.client.HTTPSConnection("us61.vintrace.net")
# Use your desired dates here:
from_date = "2025-08-20"
to_date = "2025-08-24"

# If you want a token from .env, you could use:
# from dotenv import load_dotenv
# load_dotenv()
# VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")

headers = {
    'Accept': "application/json",
    'Authorization': "Bearer j1O2r05x35QjCVMwlHV4kENMFzoWXw1y5ngNBjXFBcW-88nsU6yMYSu_glOH",
}

# Only pull the first 100 records
offset = 0
limit = 100

conString = f"/smwe/api/v6/workorders/list?fromDate={from_date}&toDate={to_date}&offset={offset}&limit={limit}&allDetailsFetched=True"
conn.request("GET", conString, headers=headers)
res = conn.getresponse()
data = res.read()
myData = json.loads(data.decode('utf-8'))

# Save to file - only first 100 results
output_dir = "Main/data/GET--jobs"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "jobs.json")
with open(output_path, "w", encoding="utf-8") as json_file:
    json.dump(myData, json_file, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(myData.get('workOrders', []))} workorders to {output_path}")