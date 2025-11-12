import json
import os
import requests

from dotenv import load_dotenv
load_dotenv()

# Get base URL from .env
BASE_URL = os.getenv("BASE_VINTRACE_SANDBOX_URL", "https://sandbox.vintrace.net")
url = f"{BASE_URL}/smwedemo/api/v7/operation/fruit-intakes"

# Example payload for fruit intake (fill in with your actual data)
payload = {
    "linkEarliestBooking": False,
    "id": 123,
    "block": {
        "id": 1,
        "name": "Block A",
        "extId": "BLK-A-2025"
    },
    "vintage": 2025,
    "bookingNumber": "BK12345",
    "owner": {
        "id": 12,
        "name": "Grower Inc",
        "extId": "GROWER-12"
    },
    "dateOccurred": 1728241200000,
    "timeIn": 1728241300000,
    "timeOut": 1728241400000,
    "weighTag": "WT-001",
    "externalWeighTag": "EXT-001",
    "winery": {
        "id": 7,
        "name": "Crest Winery",
        "businessUnit": "BW-WA-85"
    },
    "scale": {
        "id": 2,
        "name": "Scale 1",
        "extId": "SCALE-2"
    },
    "gross": {
        "value": 5000.0,
        "unit": "kg"
    },
    "tare": {
        "value": 500.0,
        "unit": "kg"
    },
    "net": {
        "value": 4500.0,
        "unit": "kg"
    },
    "jobStatus": "draft",
    "intendedProduct": {
        "id": 22,
        "name": "Cabernet Tank",
        "extId": "TANK-CAB-22"
    },
    "unitPrice": {
        "value": 1.25,
        "unit": "USD/kg"
    },
    "metrics": [
        {
            "name": "Brix",
            "interfaceMappedName": "BRIX",
            "value": 23.1,
            "nonNumericValue": ""
        },
        {
            "name": "Pass/Fail",
            "interfaceMappedName": "PF",
            "value": None,
            "nonNumericValue": "Pass"
        }
    ],
    "harvestMethod": "HAND",
    "weighMasterText": "John Doe",
    "carrier": {
        "id": 5,
        "name": "Trucking LLC",
        "extId": "CARRIER-5"
    },
    "consignmentNote": "CN-2025-001",
    "driverName": "Jane Smith",
    "lastLoad": False,
    "operatorNotes": "Fruit arrived in good condition.",
    "truckRegistration": "ABC123"
}

headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_API_TOKEN",  # Uncomment if needed
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception:
    print("Response Text:", response.text)