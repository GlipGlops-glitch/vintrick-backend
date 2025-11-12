# python tools/fetch_workorders_v7_extra_with_v6_fetch.py

import os
import json
import logging
import time
from dotenv import load_dotenv
from datetime import datetime
from utils.endpoint_caller import EndpointCaller, setup_error_logger, setup_metrics_logger

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(__name__)

logger = setup_logging()
metrics_logger = setup_metrics_logger("metrics.log")
error_logger = setup_error_logger("error.log")

def setup_all_logger(logfile="Log_All.log"):
    all_logger = logging.getLogger("all_logger")
    all_logger.setLevel(logging.INFO)
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

def date_to_epoch_ms(date_str):
    """
    Convert a date string (YYYY-MM-DD) to epoch milliseconds.
    If the date string is already epoch ms, return as int.
    """
    try:
        if date_str and date_str.isdigit() and len(date_str) > 8:
            return int(date_str)
        dt_format = "%Y-%m-%d"
        dt = datetime.strptime(date_str, dt_format)
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(dt.timestamp() * 1000)
    except Exception as e:
        logger.error(f"❌ Could not convert date '{date_str}' to epoch ms: {e}")
        all_logger.error(f"❌ Could not convert date '{date_str}' to epoch ms: {e}")
        return None

def extract_ids(work_orders):
    wo_ids = []
    job_ids = []
    for wo in work_orders:
        # Work order ID
        if "id" in wo:
            wo_ids.append(wo["id"])
        # Jobs may be a list in wo['jobs']
        for job in wo.get("jobs", []):
            if "id" in job:
                job_ids.append(job["id"])
    return wo_ids, job_ids

def filter_extraction_jobs(work_orders):
    extraction_records = []
    extraction_wo_ids_set = set()
    extraction_job_ids_set = set()
    for wo in work_orders:
        has_extraction = False
        for job in wo.get("jobs", []):
            if job.get("operationType") == "EXTRACTION":
                extraction_records.append({
                    "wo_id": wo.get("id"),
                    "wo_name": wo.get("name"),
                    "wo_status": wo.get("status"),
                    "wo_summary": wo.get("summary"),
                    "job_id": job.get("id"),
                    "job_status": job.get("status"),
                    "job_scheduledTime": job.get("scheduledTime"),
                    "job_finishedTime": job.get("finishedTime"),
                    "job_operationType": job.get("operationType"),
                })
                extraction_job_ids_set.add(job.get("id"))
                has_extraction = True
        if has_extraction and "id" in wo:
            extraction_wo_ids_set.add(wo["id"])
    return extraction_records, list(extraction_wo_ids_set), list(extraction_job_ids_set)

def print_extraction_table(records, table_path):
    if not records:
        print("No extraction jobs found.")
        return
    headers = [
        "wo_id", "wo_name", "wo_status", "wo_summary",
        "job_id", "job_status", "job_scheduledTime", "job_finishedTime", "job_operationType"
    ]
    col_widths = {h: max(len(h), max((len(str(r[h])) for r in records), default=0)) for h in headers}
    with open(table_path, "w", encoding="utf-8") as f:
        f.write(" | ".join(h.ljust(col_widths[h]) for h in headers) + "\n")
        f.write("-|-".join('-'*col_widths[h] for h in headers) + "\n")
        for r in records:
            f.write(" | ".join(str(r[h]).ljust(col_widths[h]) for h in headers) + "\n")
    print(f"Extraction jobs table saved to {table_path}")

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    endpoint_path = "/smwe/api/v7/operation/work-orders"
    url = BASE_URL + endpoint_path

    output_dir = "Main/data/GET--work_orders_paged"
    ensure_dir(output_dir)

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    limit = int(os.getenv("WORK_ORDER_LIMIT", "100"))
    offset = 0
    max_offset = int(os.getenv("WORK_ORDER_MAX_OFFSET", "10000"))
    delay_between_requests = float(os.getenv("WORKORDER_V6_DELAY_SEC", "0.5"))  # delay in seconds

    scheduled_since = os.getenv("WORK_ORDER_SCHEDULED_SINCE", "2025-08-25")
    scheduled_since_val = date_to_epoch_ms(scheduled_since) if scheduled_since else None

    logger.info(f"Fetching work orders paged using limit/offset and scheduledSince. limit={limit}, max_offset={max_offset}, scheduledSince={scheduled_since_val}")
    all_logger.info(f"Fetching work orders paged using limit/offset and scheduledSince. limit={limit}, max_offset={max_offset}, scheduledSince={scheduled_since_val}")

    endpoint_caller = EndpointCaller(
        logger=logger,
        metrics_logger=metrics_logger,
        error_logger=error_logger
    )

    all_work_orders = []
    more_data = True

    while more_data and offset < max_offset:
        params = {
            "limit": limit,
            "offset": offset,
            "scheduledSince": scheduled_since_val if scheduled_since_val else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        try:
            result = endpoint_caller.call(url, headers=headers, params=params)
            work_orders = result.get("results", [])
            logger.info(f"Retrieved {len(work_orders)} work orders [offset {offset}]")
            all_logger.info(
                f"✅ {len(work_orders)} work orders [offset {offset}] | Endpoint: {url} | Params: {params}"
            )
            all_work_orders.extend(work_orders)
            if len(work_orders) < limit:
                more_data = False
            else:
                offset += limit
        except Exception as e:
            logger.error(f"❌ Error fetching work orders (offset {offset}): {e}")
            all_logger.error(
                f"❌ Error fetching work orders (offset {offset}): {e} | Endpoint: {url} | Params: {params}"
            )
            more_data = False

    output_path = os.path.join(output_dir, "work_orders_paged.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_work_orders, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(all_work_orders)} work orders to {output_path}")
    all_logger.info(f"✅ Saved {len(all_work_orders)} work orders to {output_path} | Endpoint: {url}")

    # Extract wo_ids and job_ids lists
    wo_ids, job_ids = extract_ids(all_work_orders)
    wo_ids_path = os.path.join(output_dir, "wo_ids.json")
    job_ids_path = os.path.join(output_dir, "job_ids.json")

    with open(wo_ids_path, "w", encoding="utf-8") as f:
        json.dump(wo_ids, f, indent=2, ensure_ascii=False)
    with open(job_ids_path, "w", encoding="utf-8") as f:
        json.dump(job_ids, f, indent=2, ensure_ascii=False)

    print(f"Saved work order IDs ({len(wo_ids)}) to: {wo_ids_path}")
    print(f"Saved job IDs ({len(job_ids)}) to: {job_ids_path}")

    # --------- Improved Section: Fetch details for each wo_id from v6 endpoint ---------
    v6_details = []
    v6_errors = []
    v6_detail_dir = os.path.join(output_dir, "v6_details")
    ensure_dir(v6_detail_dir)
    v6_endpoint_base = BASE_URL + "/smwe/api/v6/workorders/"

    consecutive_errors = 0
    max_consecutive_errors = 10  # Stop if too many consecutive errors (API may be down)

    for idx, wo_id in enumerate(wo_ids):
        v6_url = v6_endpoint_base + str(wo_id)
        try:
            logger.info(f"Fetching details for wo_id {wo_id} from {v6_url}")
            detail_result = endpoint_caller.call(v6_url, headers=headers)
            v6_details.append(detail_result)
            consecutive_errors = 0  # Reset on success
            detail_path = os.path.join(v6_detail_dir, f"{wo_id}.json")
            with open(detail_path, "w", encoding="utf-8") as f:
                json.dump(detail_result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"❌ Error fetching v6 details for wo_id {wo_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response text: {getattr(e.response, 'text', '')}")
            all_logger.error(f"❌ Error fetching v6 details for wo_id {wo_id}: {e} | Endpoint: {v6_url}")
            v6_errors.append({"wo_id": wo_id, "error": str(e)})
            if consecutive_errors >= max_consecutive_errors:
                logger.error(f"Too many consecutive errors ({max_consecutive_errors})! Stopping further requests.")
                break
        time.sleep(delay_between_requests)  # Add delay between requests

    # Save all details and errors together
    v6_all_details_path = os.path.join(output_dir, "v6_workorder_details.json")
    v6_errors_path = os.path.join(output_dir, "v6_workorder_errors.json")
    with open(v6_all_details_path, "w", encoding="utf-8") as f:
        json.dump(v6_details, f, indent=2, ensure_ascii=False)
    with open(v6_errors_path, "w", encoding="utf-8") as f:
        json.dump(v6_errors, f, indent=2, ensure_ascii=False)

    print(f"Saved v6 workorder details for {len(v6_details)} workorders to: {v6_all_details_path}")
    if v6_errors:
        print(f"Errors for {len(v6_errors)} workorders saved to: {v6_errors_path}")

    # --------- Extraction jobs: table and JSON output + Extraction wo_ids & job_ids ---------
    extraction_records, extraction_wo_ids, extraction_job_ids = filter_extraction_jobs(all_work_orders)
    extraction_table_path = os.path.join(output_dir, "extraction_jobs_table.txt")
    extraction_json_path = os.path.join(output_dir, "extraction_jobs.json")
    extraction_wo_ids_path = os.path.join(output_dir, "extraction_wo_ids.json")
    extraction_job_ids_path = os.path.join(output_dir, "extraction_job_ids.json")

    print_extraction_table(extraction_records, extraction_table_path)
    with open(extraction_json_path, "w", encoding="utf-8") as f:
        json.dump(extraction_records, f, indent=2, ensure_ascii=False)
    with open(extraction_wo_ids_path, "w", encoding="utf-8") as f:
        json.dump(extraction_wo_ids, f, indent=2, ensure_ascii=False)
    with open(extraction_job_ids_path, "w", encoding="utf-8") as f:
        json.dump(extraction_job_ids, f, indent=2, ensure_ascii=False)
    print(f"Extraction jobs JSON saved to {extraction_json_path}")
    print(f"Extraction work order IDs saved to {extraction_wo_ids_path}")
    print(f"Extraction job IDs saved to {extraction_job_ids_path}")