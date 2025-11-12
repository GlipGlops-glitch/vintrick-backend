# python tools/fetch_fruit_intakes_all.py

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

    logger.info(f"Requesting ALL fruit intakes from {url} ...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        fruit_intakes = result.get("results", result)
        logger.info(f"Fetched {len(fruit_intakes)} fruit intakes")
    except Exception as e:
        logger.error(f"❌ Error fetching fruit intakes: {e}")
        fruit_intakes = []

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fruit_intakes, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(fruit_intakes)} fruit intakes to {output_path}")