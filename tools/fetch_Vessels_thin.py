# python tools/fetch_Vessels_thin.py

# python tools/fetch_Vessels_thin.py

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
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def fetch_vessels_page(url, headers, params):
    """Fetch a single page of vessels with error handling."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    if not VINTRACE_API_TOKEN:
        logger.error("No VINTRACE_API_TOKEN found in environment. Exiting.")
        exit(1)

    endpoint_path = "/smwe/api/v7/report/vessel-details-report"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--vessels"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "vessels_thin.json")

    headers = {
        "Authorization": f"Bearer {VINTRACE_API_TOKEN}"
    }

    # First, get totalResults
    params = {
        "limit": 1,
        "offset": 0
    }
    
    logger.info(f"Getting total number of vessels from {url} ...")
    try:
        result = fetch_vessels_page(url, headers, params)
        total_results = result.get("totalResults", 0)
        logger.info(f"Total vessels to fetch: {total_results}")
    except Exception as e:
        logger.error(f"❌ Error fetching totalResults: {e}")
        exit(1)

    # Now, fetch all vessels in batches
    limit = 200
    offset = 0
    all_vessels = []

    logger.info(f"Fetching all vessels ({total_results}) from {url} with paginated params")

    while offset < total_results:
        params = {
            "limit": limit,
            "offset": offset
        }
        logger.info(f"Requesting offset {offset} (Progress: {offset}/{total_results})")
        try:
            result = fetch_vessels_page(url, headers, params)
            vessels = result.get("results", [])
            
            if not vessels:
                logger.info("No more vessels returned, stopping pagination.")
                break

            all_vessels.extend(vessels)
            logger.info(f"Retrieved {len(vessels)} vessels at offset {offset}")

            offset += limit

        except Exception as e:
            logger.error(f"❌ Error fetching vessels at offset {offset}: {e}")
            logger.warning(f"Partial data saved: {len(all_vessels)} vessels collected so far")
            break

    # Save all vessels
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_vessels, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(all_vessels)} vessels to {output_path}")
    except IOError as e:
        logger.error(f"❌ Error writing vessels file: {e}")
        exit(1)

    # Write first 10 records to a sample file
    sample_output_path = os.path.join(output_dir, "vessels_thin_sample.json")
    sample_vessels = all_vessels[:10] if len(all_vessels) >= 10 else all_vessels
    try:
        with open(sample_output_path, "w", encoding="utf-8") as f:
            json.dump(sample_vessels, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(sample_vessels)} sample vessels to {sample_output_path}")
    except IOError as e:
        logger.error(f"❌ Error writing sample file: {e}")

    # Final summary
    logger.info("\n" + "="*60)
    logger.info("FETCH SUMMARY")
    logger.info("="*60)
    logger.info(f"Total vessels fetched: {len(all_vessels)}")
    logger.info("="*60)