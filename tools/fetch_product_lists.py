# python tools/fetch_product_lists.py

import os
import requests
import json
from dotenv import load_dotenv

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def fetch_product_list(url, token, first=None, max_=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {}
    if first is not None:
        params["first"] = str(first)
    if max_ is not None:
        params["max"] = str(max_)

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    endpoint_path = "/smwe/api/v6/products/list"
    url = BASE_URL + endpoint_path

    # You can use env vars, CLI args, or hard-code these as needed
    first = os.getenv("VINTRACE_FIRST", 50)  # Example: default to 10
    max_ = os.getenv("VINTRACE_MAX", 100)     # Example: default to 30

    output_dir = "Main/data/GET--product_lists"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "product_list.json")

    if not VINTRACE_API_TOKEN:
        print("Error: VINTRACE_API_TOKEN is not set in environment variables.")
        exit(1)

    try:
        product_list = fetch_product_list(url, VINTRACE_API_TOKEN, first, max_)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(product_list, f, indent=2)
        print(f"Product list saved to {output_path}")
    except Exception as e:
        print(f"Failed to fetch product list: {e}")