# vintrick-backend/tools/test_fetch_one_shipment.py
# Usage: python tools/test_fetch_one_shipment.py

import os
import json
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")
    endpoint_path = "/smwe/api/v7/operation/shipments"
    url = BASE_URL + endpoint_path

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # Fetch just one shipment
    params = {
        "limit": 1,
        "offset": 0,
        "include": "allocations,composition,cost"
    }

    print(f"Requesting: {url} with params {params}")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        shipments = result.get("results", [])
        if shipments:
            print("Shipment data:")
            print(json.dumps(shipments[0], indent=2, ensure_ascii=False))
        else:
            print("No shipment data returned.")
    except Exception as e:
        print(f"❌ Error fetching shipment: {e}")

if __name__ == "__main__":
    main()