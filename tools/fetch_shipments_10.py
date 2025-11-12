#python tools/fetch_shipments_10.py

import os
import json
import logging
from dotenv import load_dotenv
import requests

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    endpoint_path = "/smwe/api/v7/operation/shipments"
    url = BASE_URL + endpoint_path

    # Output to Main/data/GET--shipments under project root
    output_dir = "Main/data/GET--shipments"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "10_shipments.json")

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # Fetch the 10 most recent shipments
    params = {
        "include": "allocations,composition,cost",
        "limit": 10,
        "offset": 0,
        "orderBy": "occurredTime",
        "orderDirection": "desc"
    }
    logger.info(f"Fetching the 10 most recent shipments from {url} ...")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        shipments = result.get("results", [])
        logger.info(f"Retrieved {len(shipments)} shipments")
    except Exception as e:
        logger.error(f"❌ Error fetching shipments: {e}")
        shipments = []

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(shipments, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(shipments)} shipments to {output_path}")