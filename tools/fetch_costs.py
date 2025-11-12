#python tools/fetch_costs.py

import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
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

def dates_inclusive(start_date, end_date):
    """Yield each date from start_date to end_date inclusive."""
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)

def date_to_epoch_ms(d, end=False):
    """Convert a date to epoch milliseconds in UTC. If end=True, use 23:59:59.999."""
    if end:
        dt = datetime(d.year, d.month, d.day, 23, 59, 59, 999000, tzinfo=timezone.utc)
    else:
        dt = datetime(d.year, d.month, d.day, 0, 0, 0, 0, tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

def fetch_all_pages(session, base_url, initial_url, headers, params):
    """
    Fetch all pages for a paginated endpoint that returns:
      - results: array
      - next: string or null (path to next page, e.g. '/.../business-unit-transactions?offset=10&limit=10')
    """
    all_results = []
    url = initial_url
    page = 1
    working_params = dict(params) if params else None

    while True:
        resp = session.get(url, headers=headers, params=working_params)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            msg = f"{e} | status={resp.status_code}"
            try:
                msg += f" | body={resp.text}"
            except Exception:
                pass
            raise RuntimeError(msg)

        payload = resp.json() if resp.content else {}
        results = payload.get("results", [])
        total = payload.get("totalResults")
        nxt = payload.get("next")

        all_results.extend(results)
        logger.info(
            f"Page {page}: got {len(results)} results (total so far: {len(all_results)})"
            + (f", totalResults={total}" if total is not None else "")
        )

        if not nxt:
            break

        # Build the absolute URL for the next page and clear params so we don't double-append
        url = urljoin(base_url, nxt)
        working_params = None  # 'next' already includes query string
        page += 1

    return all_results

def fetch_all_pages_with_limit_autotune(session, base_url, url, headers, base_params, limit_candidates):
    """
    Try the request with each limit in limit_candidates until one succeeds.
    Returns (results, chosen_limit).
    If failure is not related to "limit greater than max", re-raises the error.
    """
    last_err = None
    for lim in limit_candidates:
        params = dict(base_params)
        params["limit"] = lim
        # Offset is redundant when using 'next' links but harmless to include at 0
        params["offset"] = 0

        try:
            logger.info(f"Trying request with limit={lim} ...")
            results = fetch_all_pages(session, base_url, url, headers, params)
            logger.info(f"Request with limit={lim} succeeded.")
            return results, lim
        except RuntimeError as e:
            msg = str(e)
            # Detect the specific "limit greater than the max" error from API
            if "Limit can't be zero or negative, or greater than the max limit" in msg:
                logger.warning(f"Limit {lim} rejected by API. Trying lower limit...")
                last_err = e
                continue
            # Some other error -> re-raise
            raise

    # If we exhausted all candidates, raise the last known error (or a generic one)
    if last_err:
        raise last_err
    raise RuntimeError("Failed to fetch pages with any limit candidate (no specific error captured).")

if __name__ == "__main__":
    load_dotenv()

    # ========= USER CONFIG (set these two to override env vars) =========
    # Example: "2025-07-01" .. "2025-08-01"
    DATE_FROM_OVERRIDE = "2025-01-01"  # e.g., "2025-07-01"
    DATE_TO_OVERRIDE = "2025-08-26"    # e.g., "2025-08-01"
    # ====================================================================

    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net").rstrip("/")

    endpoint_path = "/smwe/api/v7/costs/business-unit-transactions"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--business_unit_transactions_by_day"
    ensure_dir(output_dir)

    headers = {"Accept": "application/json"}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"
    else:
        logger.warning("VINTRACE_API_TOKEN is not set. Requests will likely fail with 401 Unauthorized.")

    # Optional filters (set via env if needed)
    business_unit = os.getenv("VINTRACE_BUSINESS_UNIT")   # e.g. 'US57'
    winery_id = os.getenv("VINTRACE_WINERY_ID")           # e.g. '7177'
    winery_name = os.getenv("VINTRACE_WINERY_NAME")       # e.g. 'Z Winery'

    # Candidate limits to try automatically. Override with env if desired.
    # The API rejected 1000 in your logs. These candidates step down until success.
    env_candidates = os.getenv("BUSINESS_UNIT_TRANSACTIONS_LIMIT_CANDIDATES", "")
    if env_candidates.strip():
        try:
            LIMIT_CANDIDATES = [int(x) for x in env_candidates.split(",") if x.strip()]
        except ValueError:
            logger.warning("Invalid BUSINESS_UNIT_TRANSACTIONS_LIMIT_CANDIDATES. Falling back to defaults.")
            LIMIT_CANDIDATES = [200, 100, 50, 25, 10, 5, 1]
    else:
        LIMIT_CANDIDATES = [200, 100, 50, 25, 10, 5, 1]

    # Date range (YYYY-MM-DD). Use override first, then env, else error.
    date_from_str = DATE_FROM_OVERRIDE or os.getenv("BUSINESS_UNIT_TRANSACTIONS_DATE_FROM", "")
    date_to_str = DATE_TO_OVERRIDE or os.getenv("BUSINESS_UNIT_TRANSACTIONS_DATE_TO", "")

    if not date_from_str or not date_to_str:
        logger.error("❌ Please set DATE_FROM_OVERRIDE and DATE_TO_OVERRIDE, or the env vars BUSINESS_UNIT_TRANSACTIONS_DATE_FROM and BUSINESS_UNIT_TRANSACTIONS_DATE_TO (YYYY-MM-DD).")
        raise SystemExit(1)

    try:
        date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
    except Exception as e:
        logger.error(f"❌ Invalid date format. Use YYYY-MM-DD. Details: {e}")
        raise SystemExit(1)

    if date_from > date_to:
        logger.error("❌ Date range invalid: start date is after end date.")
        raise SystemExit(1)

    logger.info(f"Fetching business unit transactions daily from {date_from_str} to {date_to_str}...")

    session = requests.Session()

    discovered_working_limit = None

    for day in dates_inclusive(date_from, date_to):
        start_ms = date_to_epoch_ms(day, end=False)
        end_ms = date_to_epoch_ms(day, end=True)
        day_str = day.strftime("%Y-%m-%d")

        base_params = {
            "startDate": start_ms,  # API expects int64 epoch millis
            "endDate": end_ms,      # API expects int64 epoch millis
        }
        if business_unit:
            base_params["businessUnit"] = business_unit
        if winery_id:
            try:
                base_params["wineryId"] = int(winery_id)
            except ValueError:
                base_params["wineryId"] = winery_id
        if winery_name:
            base_params["wineryName"] = winery_name

        logger.info(f"Fetching business unit transactions for {day_str} (ms: {start_ms}..{end_ms})")

        try:
            # If we've already discovered a working limit, use it directly for speed
            if discovered_working_limit is not None:
                params = dict(base_params)
                params["limit"] = discovered_working_limit
                params["offset"] = 0
                results = fetch_all_pages(session, BASE_URL, url, headers, params)
            else:
                results, chosen_limit = fetch_all_pages_with_limit_autotune(
                    session=session,
                    base_url=BASE_URL,
                    url=url,
                    headers=headers,
                    base_params=base_params,
                    limit_candidates=LIMIT_CANDIDATES,
                )
                discovered_working_limit = chosen_limit
                logger.info(f"Using discovered max working limit={discovered_working_limit} for remaining days.")

            logger.info(f"Retrieved {len(results)} transactions for {day_str}")
        except Exception as e:
            logger.error(f"❌ Error fetching transactions for {day_str}: {e}")
            results = []

        output_path = os.path.join(output_dir, f"business_unit_transactions_{day_str}.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(results)} records to {output_path}")
        except Exception as e:
            logger.error(f"❌ Failed saving results to {output_path}: {e}")