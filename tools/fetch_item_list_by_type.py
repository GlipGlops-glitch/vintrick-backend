# python tools/fetch_item_list_by_type.py

import os
import requests
import json
from dotenv import load_dotenv

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def fetch_item_list(base_url, token, first=None, max_=None):
    endpoint_path = "/smwe/api/v6/search/list/?type=vessel&first=10"
    url = base_url + endpoint_path
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    # Set from env vars, or defaults
    first = os.getenv("VINTRACE_FIRST", 10)
    max_ = os.getenv("VINTRACE_MAX", 10)

    output_dir = "Main/data/GET--Item_lists"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "Item_list.json")

    if not VINTRACE_API_TOKEN:
        print("Error: VINTRACE_API_TOKEN is not set in environment variables.")
        exit(1)

    try:
        item_list = fetch_item_list(BASE_URL, VINTRACE_API_TOKEN, first, max_)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(item_list, f, indent=2)
        print(f"Item list saved to {output_path}")
    except Exception as e:
        print(f"Failed to fetch item list: {e}")