
#python tools/fetch_wo_v6.py

import os
import json
import logging
import datetime
import re
from dotenv import load_dotenv
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

def extract_endpoint_urls(workorders):
    jobs_urls = []
    wo_urls = []
    # Patterns for matching endpoint URLs
    job_pattern = re.compile(r"^/smwe/api/v6/workorders/jobs/\d+$")
    wo_pattern = re.compile(r"^/smwe/api/v6/workorders/\d+$")
    for wo in workorders:
        # Workorder-level endpoint
        wo_url = wo.get("endpointURL")
        if wo_url and wo_pattern.match(wo_url):
            wo_urls.append(wo_url)
        # Job-level endpoints
        for job in wo.get("jobs", []):
            job_url = job.get("endpointURL")
            if job_url and job_pattern.match(job_url):
                jobs_urls.append(job_url)
    return jobs_urls, wo_urls

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")
    endpoint_path = "/smwe/api/v6/workorders/list/"
    url = BASE_URL + endpoint_path
    output_dir = "Main/data/GET--WO_v6"
    ensure_dir(output_dir)
    headers = {
        "Authorization": f"Bearer {VINTRACE_API_TOKEN}",
        "Accept": "application/json"
    }

    # Configurable or default parameters
    max_results = int(os.getenv("WO_MAX", "200"))
    from_date = os.getenv("WO_FROMDATE", "2025-07-01")
    to_date = os.getenv("WO_TODATE", "2025-07-25")
    work_order_state = "COMPLETE"  # Added param

    if not from_date:
        from_date = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    if not to_date:
        to_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    # Send pagination params to get more results if supported by API
    params = {
        "fromDate": from_date,
        "toDate": to_date,
        "first": "0",
        "max": str(max_results),
        "workOrderState": work_order_state
    }

    print("\n--- DEBUG: API CALL ---")
    print(f"URL:         {url}")
    print(f"Headers:     {headers}")
    print(f"Params:      {params}\n")

    logger.info(f"Fetching v6 workorders from {url} with params {params}")
    all_logger.info(f"Fetching v6 workorders from {url} with params {params}")

    endpoint_caller = EndpointCaller(
        logger=logger,
        metrics_logger=metrics_logger,
        error_logger=error_logger
    )

    try:
        result = endpoint_caller.call(url, headers=headers, params=params)
        workorders = result.get("workOrders", []) if isinstance(result, dict) else []
        logger.info(f"Retrieved {len(workorders)} workorders")
        all_logger.info(
            f"✅ {len(workorders)} workorders | Endpoint: {url} | Params: {params}"
        )
    except Exception as e:
        logger.error(f"❌ Error fetching workorders: {e}")
        all_logger.error(
            f"❌ Error fetching workorders: {e} | Endpoint: {url} | Params: {params}"
        )
        workorders = []

    output_path = os.path.join(output_dir, "wo_v6.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workorders, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(workorders)} workorders to {output_path}")
    all_logger.info(f"✅ Saved {len(workorders)} workorders to {output_path} | Endpoint: {url}")

    # --- Extract endpoint URLs and save ---
    jobs_urls, wo_urls = extract_endpoint_urls(workorders)

    jobs_urls_path = os.path.join(output_dir, "job_endpointurls.json")
    wo_urls_path = os.path.join(output_dir, "wo_endpointurls.json")
    with open(jobs_urls_path, "w", encoding="utf-8") as f:
        json.dump(jobs_urls, f, indent=2, ensure_ascii=False)
    with open(wo_urls_path, "w", encoding="utf-8") as f:
        json.dump(wo_urls, f, indent=2, ensure_ascii=False)

    print(f"\nSaved job endpoint URLs ({len(jobs_urls)}) to: {jobs_urls_path}")
    print(f"Saved workorder endpoint URLs ({len(wo_urls)}) to: {wo_urls_path}")