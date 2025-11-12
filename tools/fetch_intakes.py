
#python tools/fetch_intakes.py

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

    endpoint_path = "/smwe/api/v7/operation/bulk-intakes"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--intakes"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "intakes.json")

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # First, get totalResults
    params = {
        "limit": 1,
        "offset": 0
    }
    logger.info(f"Getting total number of intakes from {url} ...")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        total_results = result.get("totalResults", 0)
    except Exception as e:
        logger.error(f"❌ Error fetching totalResults: {e}")
        total_results = 0

    # Now, fetch all intakes in batches
    limit = 200
    offset = 0
    all_intakes = []

    logger.info(f"Fetching all intakes ({total_results}) from {url} with paginated params")

    while offset < total_results:
        params = {
            "limit": limit,
            "offset": offset,
        }
        logger.info(f"Requesting offset {offset}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            intakes = result.get("results", [])
            if not intakes:
                logger.info("No more intakes returned, stopping pagination.")
                break

            all_intakes.extend(intakes)
            logger.info(f"Retrieved {len(intakes)} intakes at offset {offset}")

            offset += limit

        except Exception as e:
            logger.error(f"❌ Error fetching intakes at offset {offset}: {e}")
            break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_intakes, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(all_intakes)} intakes to {output_path}")