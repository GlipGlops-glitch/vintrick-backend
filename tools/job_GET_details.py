#python tools/job_GET_details.py

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

    # Input: List of job IDs to fetch
    job_ids = [
        # Example job IDs; replace with real values or load dynamically
        177995
    ]

    endpoint_template = "/smwe/api/v6/workorders/jobs/{jobId}"
    output_dir = "Main/data/GET--job-details"
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "job_details.json")

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    all_job_details = []

    for job_id in job_ids:
        endpoint_path = endpoint_template.format(jobId=job_id)
        url = BASE_URL + endpoint_path
        logger.info(f"Fetching job details for jobId: {job_id} from {url}")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            job_detail = response.json()
            all_job_details.append(job_detail)
            logger.info(f"Retrieved job details for jobId: {job_id}")
        except Exception as e:
            logger.error(f"❌ Error fetching job details for jobId {job_id}: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_job_details, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved details for {len(all_job_details)} jobs to {output_path}")