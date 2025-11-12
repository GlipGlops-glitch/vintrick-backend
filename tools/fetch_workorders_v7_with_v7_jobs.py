# python tools/fetch_workorders_v7_with_v7_jobs.py

import os
import json
import logging
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

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    # Path to the input work orders JSON
    input_path = "Main/data/GET--work_orders_paged/work_orders_paged.json"
    output_dir = "Main/data/GET--work_orders_paged"
    ensure_dir(output_dir)

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # Read in work orders from json
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            all_work_orders = json.load(f)
        logger.info(f"Loaded {len(all_work_orders)} work orders from {input_path}")
        all_logger.info(f"Loaded {len(all_work_orders)} work orders from {input_path}")
    except Exception as e:
        logger.error(f"❌ Could not load work orders: {e}")
        all_logger.error(f"❌ Could not load work orders: {e}")
        exit(1)

    endpoint_caller = EndpointCaller(
        logger=logger,
        metrics_logger=metrics_logger,
        error_logger=error_logger
    )

    # Fetch job details using lowercased operationType and job_id from jobs in each work order
    job_details = []
    for wo in all_work_orders:
        jobs = wo.get("jobs", [])
        for job in jobs:
            job_id = job.get("id")
            operation_type = job.get("operationType")
            if job_id and operation_type:
                operation_type_lower = str(operation_type).lower()
                job_url = f"{BASE_URL}/smwe/api/v7/operation/{operation_type_lower}/job:{job_id}"
                try:
                    job_result = endpoint_caller.call(job_url, headers=headers)
                    logger.info(f"Retrieved job {job_id} with operationType {operation_type_lower}")
                    all_logger.info(
                        f"✅ Retrieved job {job_id} with operationType {operation_type_lower} | Endpoint: {job_url}"
                    )
                    job_details.append({
                        "job_id": job_id,
                        "operationType": operation_type,
                        "operationType_lower": operation_type_lower,
                        "result": job_result
                    })
                except Exception as e:
                    logger.error(f"❌ Error fetching job {job_id} (operationType {operation_type_lower}): {e}")
                    all_logger.error(
                        f"❌ Error fetching job {job_id} (operationType {operation_type_lower}): {e} | Endpoint: {job_url}"
                    )

    jobs_details_path = os.path.join(output_dir, "jobs_details.json")
    with open(jobs_details_path, "w", encoding="utf-8") as f:
        json.dump(job_details, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved job details for {len(job_details)} jobs to {jobs_details_path}")
    all_logger.info(f"✅ Saved job details for {len(job_details)} jobs to {jobs_details_path}")
    print(f"Saved job details for {len(job_details)} jobs to: {jobs_details_path}")

    # Output a sample of 50 records for testing
    sample_size = 50
    jobs_details_sample = job_details[:sample_size]
    jobs_details_sample_path = os.path.join(output_dir, "jobs_details_sample.json")
    with open(jobs_details_sample_path, "w", encoding="utf-8") as f:
        json.dump(jobs_details_sample, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved sample ({len(jobs_details_sample)}) job details to {jobs_details_sample_path}")
    all_logger.info(f"✅ Saved sample ({len(jobs_details_sample)}) job details to {jobs_details_sample_path}")
    print(f"Saved sample ({len(jobs_details_sample)}) job details to: {jobs_details_sample_path}")