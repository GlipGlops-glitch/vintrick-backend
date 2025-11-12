# python tools/fetch_transactions_sandbox.py

import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
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

def daterange(start_date, end_date):
    """Yield each date from start_date to end_date (inclusive)."""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)



if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_SANDBOX_URL", "https://sandbox.vintrace.net")

    endpoint_path = "/smwedemo/api/v6/transaction/search/"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--transactions_by_day_sandbox"
    ensure_dir(output_dir)

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # Set your date range here or via environment variables
    date_from_str = os.getenv("TRANSACTION_DATE_FROM", "2025-08-25")
    date_to_str = os.getenv("TRANSACTION_DATE_TO", "2025-08-26")

    try:
        date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
    except Exception as e:
        logger.error(f"❌ Invalid date format in TRANSACTION_DATE_FROM or TRANSACTION_DATE_TO: {e}")
        exit(1)

    logger.info(f"Fetching transactions from {date_from_str} to {date_to_str}, one file per day...")

    for single_date in daterange(date_from, date_to):
        day_str = single_date.strftime("%Y-%m-%d")
        params = {
            "dateFrom": day_str,
            "dateTo": day_str
        }
        logger.info(f"Fetching transactions for {day_str}")

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            transaction_summaries = result.get("transactionSummaries", [])
            logger.info(f"Retrieved {len(transaction_summaries)} transaction summaries for {day_str}")
        except Exception as e:
            logger.error(f"❌ Error fetching transactions for {day_str}: {e}")
            transaction_summaries = []

        output_path = os.path.join(output_dir, f"transactions_{day_str}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transaction_summaries, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(transaction_summaries)} transactions to {output_path}")