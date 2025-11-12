#   python tools/fetch_fruit_intakes_current.py

import os
import json
import logging
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta, timezone

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

def get_epoch_ms_for_today_1am():
    # Get today's date at 1am UTC
    now = datetime.now(timezone.utc)
    today_1am = datetime(year=now.year, month=now.month, day=now.day, hour=1, minute=0, second=0, tzinfo=timezone.utc)
    return int(today_1am.timestamp()) * 1000

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")

    # ---- Production vs Sandbox URL ----
    # BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net") # Production URL
    # endpoint_path = "/smwe/api/v6/intake-operations/search"

    BASE_URL = os.getenv("BASE_VINTRACE_SANDBOX_URL", "https://sandbox.vintrace.net")  #SandBox URL for testing
    endpoint_path = "/smwedemo/api/v6/intake-operations/search"


    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--fruit_intakes"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "fruit_intakes.json")

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # Calculate epoch ms for 1am today UTC
    recordedAfter = get_epoch_ms_for_today_1am()

    # First, get totalResults if available
    params = {
        "maxResults": 1,
        "firstResult": 0,
        "recordedAfter": recordedAfter
    }
    logger.info(f"Getting total number of fruit intakes from {url} ...")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        total_results = result.get("resultCount") or result.get("totalCount") or 0
    except Exception as e:
        logger.error(f"❌ Error fetching totalResults: {e}")
        total_results = 0

    # Now, fetch all fruit intakes in batches
    maxResults = 200
    firstResult = 0
    all_fruit_intakes = []

    logger.info(f"Fetching all fruit intakes ({total_results}) from {url} with paginated params")

    while firstResult < total_results:
        params = {
            "maxResults": maxResults,
            "firstResult": firstResult,
            "recordedAfter": recordedAfter
        }
        logger.info(f"Requesting firstResult {firstResult}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            fruit_intakes = result.get("intakes", [])
            if not fruit_intakes:
                logger.info("No more fruit intakes returned, stopping pagination.")
                break

            all_fruit_intakes.extend(fruit_intakes)
            logger.info(f"Retrieved {len(fruit_intakes)} fruit intakes at firstResult {firstResult}")

            firstResult += maxResults

        except Exception as e:
            logger.error(f"❌ Error fetching fruit intakes at firstResult {firstResult}: {e}")
            break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_fruit_intakes, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(all_fruit_intakes)} fruit intakes to {output_path}")