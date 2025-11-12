import os
import requests
import json

# Load environment variables
BASE_URL = os.getenv("BASE_VINTRACE_SANDBOX_URL", "https://sandbox.vintrace.net")
VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {VINTRACE_API_TOKEN}",
}

# Example payload for api/v6/workorders/jobs/submit
payload = {
    "jobId": 1234,
    "submitType": "completed",
    "dateStarted": "2025-08-24T19:26:22Z",
    "fields": [
        {
            "fieldId": "FIELD001",
            "value": "Sample Value",
            "dataType": "string",
            "parentFieldId": "PARENT001",
            "selectedValues": [
                {
                    "id": 1001,
                    "name": "Option A",
                    "type": "select",
                    "code": "A",
                    "fillType": "manual",
                    "checked": True,
                    "amount": "5",
                    "preferred": False
                }
            ]
        }
    ]
}

url = f"{BASE_URL}/api/v6/workorders/jobs/submit"

response = requests.post(url, headers=headers, data=json.dumps(payload))

print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception:
    print("Response Text:", response.text)