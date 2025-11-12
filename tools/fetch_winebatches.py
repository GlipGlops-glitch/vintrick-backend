# vintrick-backend/tools/fetch_winebatches.py
# python tools/fetch_winebatches.py

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

    if not VINTRACE_API_TOKEN:
        logger.error("No VINTRACE_API_TOKEN found in environment. Exiting.")
        exit(1)

    endpoint_path = "/smwe/api/v7/operation/wine-batches"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--winebatches"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "winebatches.json")

    headers = {
        "Authorization": f"Bearer {VINTRACE_API_TOKEN}"
    }

    # First, get totalResults
    params = {
        "limit": 1,
        "offset": 0,
        "include": "vessels"

    }
    logger.info(f"Getting total number of winebatches from {url} ...")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        total_results = result.get("totalResults", 0)
    except Exception as e:
        logger.error(f"❌ Error fetching totalResults: {e}")
        total_results = 0

    # Now, fetch all winebatches in batches
    limit = 200
    offset = 0
    all_winebatches = []

    logger.info(f"Fetching all winebatches ({total_results}) from {url} with paginated params")

    while offset < total_results:
        params = {
            "include": "vessels",
            "limit": limit,
            "offset": offset,

        }
        logger.info(f"Requesting offset {offset}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()

            winebatches = result.get("results", [])
            if not winebatches:
                logger.info("No more winebatches returned, stopping pagination.")
                break

            all_winebatches.extend(winebatches)
            logger.info(f"Retrieved {len(winebatches)} winebatches at offset {offset}")

            offset += limit

        except Exception as e:
            logger.error(f"❌ Error fetching winebatches at offset {offset}: {e}")
            break

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_winebatches, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(all_winebatches)} winebatches to {output_path}")

    # Write first 10 records to a sample file
    sample_output_path = os.path.join(output_dir, "winebatches_sample.json")
    sample_winebatches = all_winebatches[:10] if len(all_winebatches) >= 10 else all_winebatches
    with open(sample_output_path, "w", encoding="utf-8") as f:
        json.dump(sample_winebatches, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(sample_winebatches)} sample winebatches to {sample_output_path}")