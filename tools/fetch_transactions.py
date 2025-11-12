# python tools/fetch_transactions.py

import os
import json
import logging
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

from utils.endpoint_caller import setup_error_logger, setup_metrics_logger

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(__name__)

logger = setup_logging()
metrics_logger = setup_metrics_logger("metrics.log")
error_logger = setup_error_logger("error.log")

# --- Unified log for all events ---
def setup_all_logger(logfile="Log_All.log"):
    all_logger = logging.getLogger("all_logger")
    all_logger.setLevel(logging.INFO)
    # Avoid duplicate handlers
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith(logfile) for h in all_logger.handlers):
        fh = logging.FileHandler(logfile, encoding="utf-8")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        all_logger.addHandler(fh)
    return all_logger

all_logger = setup_all_logger("Log_All.log")

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
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    endpoint_path = "/smwe/api/v6/transaction/search/"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--transactions_by_day"
    ensure_dir(output_dir)

    headers = {
        "Authorization": f"Bearer {VINTRACE_API_TOKEN}",
        "Accept": "application/json"
    }
    # Set your date range here or via environment variables
    date_from_str = os.getenv("TRANSACTION_DATE_FROM", "2025-10-01")
    date_to_str = os.getenv("TRANSACTION_DATE_TO", "2025-11-11")

    try:
        date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
    except Exception as e:
        logger.error(f"❌ Invalid date format in TRANSACTION_DATE_FROM or TRANSACTION_DATE_TO: {e}")
        all_logger.error(f"❌ Invalid date format in TRANSACTION_DATE_FROM or TRANSACTION_DATE_TO: {e}")
        exit(1)

    logger.info(f"Fetching transactions from {date_from_str} to {date_to_str}, one file per day...")
    all_logger.info(f"Fetching transactions from {date_from_str} to {date_to_str}, one file per day...")

    # Use a requests.Session for persistent connection and performance
    session = requests.Session()
    session.headers.update(headers)

    for single_date in daterange(date_from, date_to):
        day_str = single_date.strftime("%Y-%m-%d")
        params = {
            "dateFrom": day_str,
            "dateTo": day_str
        }

        # Debug print of API call
        print("\n--- DEBUG: API CALL ---")
        print(f"URL:      {url}")
        print(f"Headers:  {session.headers}")
        print(f"Params:   {params}\n")

        logger.info(f"Fetching transactions for {day_str}")
        all_logger.info(f"Fetching transactions for {day_str} | Endpoint: {url} | Params: {params}")

        try:
            response = session.get(url, params=params)
            logger.info(f"HTTP Status: {response.status_code}")
            print(f"HTTP Status: {response.status_code}")
            print(f"Response Text (first 500 chars):\n{response.text[:500]}\n")
            response.raise_for_status()
            result = response.json()
            transaction_summaries = result.get("transactionSummaries", [])
            logger.info(f"Retrieved {len(transaction_summaries)} transaction summaries for {day_str}")
            all_logger.info(
                f"✅ {len(transaction_summaries)} transactions for {day_str} | Endpoint: {url} | Params: {params}"
            )
        except Exception as e:
            logger.error(f"❌ Error fetching transactions for {day_str}: {e}")
            all_logger.error(
                f"❌ Error fetching transactions for {day_str}: {e} | Endpoint: {url} | Params: {params}"
            )
            transaction_summaries = []

        output_path = os.path.join(output_dir, f"transactions_{day_str}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transaction_summaries, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(transaction_summaries)} transactions to {output_path}")
        all_logger.info(f"✅ Saved {len(transaction_summaries)} transactions to {output_path} | Endpoint: {url} | Params: {params}")