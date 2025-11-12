
#python tools/fetch_wo_v6_simple.py

import os
import requests
from dotenv import load_dotenv

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def fetch_workorders():
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")
    endpoint_path = "/smwe/api/v6/workorders/list/"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--WO_v6"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "intakes.json")

    headers = {
        "Authorization": f"Bearer {VINTRACE_API_TOKEN}",
        "Accept": "application/json"
    }

    # Print API call for debugging
    print("\n--- DEBUG: API CALL ---")
    print(f"URL:      {url}")
    print(f"Headers:  {headers}")
    print(f"Params:   None\n")

    response = requests.get(url, headers=headers)
    print(f"HTTP Status: {response.status_code}")
    print(f"Response Text (first 500 chars):\n{response.text[:500]}\n")

    response.raise_for_status()

    data = response.json()
    with open(output_path, "w") as f:
        f.write(response.text)

    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    fetch_workorders()