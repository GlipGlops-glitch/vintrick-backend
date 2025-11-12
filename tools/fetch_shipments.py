# vintrick-backend/tools/fetch_shipments.py
# python tools/fetch_shipments.py

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

    output_dir = "vintrick-backend/Main/data/GET--shipments"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "10_shipments.json")

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # First, get totalResults
    params = {
        "limit": 1,
        "offset": 0
    }
    logger.info(f"Getting total number of shipments from {url} ...")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        total_results = result.get("totalResults", 0)
    except Exception as e:
        logger.error(f"❌ Error fetching totalResults: {e}")
        total_results = 0

    # Now, fetch all shipments in batches
    limit = 10
    offset = 0
    all_shipments = []

    logger.info(f"Fetching all shipments ({total_results}) from {url} with paginated params")

    while offset < total_results:
        params = {
            "include": "allocations,composition,cost",
            "limit": limit,
            "offset": offset,
        }
        logger.info(f"Requesting offset {offset}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            shipments = result.get("results", [])
            if not shipments:
                logger.info("No more shipments returned, stopping pagination.")
                break

            all_shipments.extend(shipments)
            logger.info(f"Retrieved {len(shipments)} shipments at offset {offset}")

            offset += limit

        except Exception as e:
            logger.error(f"❌ Error fetching shipments at offset {offset}: {e}")
            break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_shipments, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(all_shipments)} shipments to {output_path}")