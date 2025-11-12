# python tools/fetch_fruit_intakes.py

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

    endpoint_path = "/smwe/api/v6/intake-operations/search"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--fruit_intakes"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "fruit_intakes.json")

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # Get totalResults (and confirm keys)
    params = {
        "maxResults": 1,
        "firstResult": 0
    }
    logger.info(f"Getting total number of fruit intakes from {url} ...")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        # Try all likely keys for counts
        total_results = (
            result.get("resultCount") or
            result.get("totalCount") or
            result.get("count") or
            result.get("total") or
            0
        )
        logger.info(f"Response keys: {list(result.keys())}")
    except Exception as e:
        logger.error(f"❌ Error fetching totalResults: {e}")
        total_results = 0

    if total_results == 0:
        logger.warning("⚠️ API reported zero fruit intakes. Check API or parameters.")

    # Fetch all fruit intakes in batches
    maxResults = 100  # API likely only returns 100 per request!
    firstResult = 0
    all_fruit_intakes = []

    logger.info(f"Fetching all fruit intakes ({total_results}) from {url} with paginated params")

    while firstResult < total_results:
        params = {
            "maxResults": maxResults,
            "firstResult": firstResult,
        }
        logger.info(f"Requesting firstResult {firstResult}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            fruit_intakes = result.get("intakes", [])
            if not isinstance(fruit_intakes, list):
                logger.error(f"❌ Unexpected result structure: {result}")
                break

            all_fruit_intakes.extend(fruit_intakes)
            logger.info(f"Retrieved {len(fruit_intakes)} fruit intakes at firstResult {firstResult}")

            # If no fruit_intakes are returned, break
            if not fruit_intakes:
                logger.info("No more fruit intakes returned, stopping pagination.")
                break

            firstResult += len(fruit_intakes)  # Always increment by what you received

        except Exception as e:
            logger.error(f"❌ Error fetching fruit intakes at firstResult {firstResult}: {e}")
            break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_fruit_intakes, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(all_fruit_intakes)} fruit intakes to {output_path}")