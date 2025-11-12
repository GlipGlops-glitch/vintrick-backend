#python tools/job_GET.py
import os
import json
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import requests

def setup_logging() -> logging.Logger:
    """Configure and return the logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def ensure_dir(dir_path: str) -> None:
    """Ensure the existence of a directory."""
    abs_path = os.path.abspath(dir_path)
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)

def extract_selected_values(selected_values: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Extract selected value dicts from a list."""
    return [
        {
            "id": sv.get("id"),
            "name": sv.get("name"),
            "dataType": sv.get("dataType"),
            "code": sv.get("code"),
            "fillType": sv.get("fillType"),
            "fillTypeDisplay": sv.get("fillTypeDisplay"),
            "confirmed": sv.get("confirmed"),
            "amount": sv.get("amount"),
            "extraDetailKey": sv.get("extraDetailKey"),
            "preferred": sv.get("preferred"),
            "breakdownMap": sv.get("breakdownMap"),
            "additionalDetails": sv.get("additionalDetails"),
        }
        for sv in selected_values or []
    ]

def extract_fields(fields: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Extract fields dicts from a list."""
    return [
        {
            "fieldId": f.get("fieldId"),
            "fieldName": f.get("fieldName"),
            "fieldType": f.get("fieldType"),
            "dataType": f.get("dataType"),
            "mandatory": f.get("mandatory"),
            "minSelections": f.get("minSelections"),
            "maxSelections": f.get("maxSelections"),
            "selectedValues": extract_selected_values(f.get("selectedValues")),
            "stringValue": f.get("stringValue"),
        }
        for f in fields or []
    ]

def extract_steps(steps: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Extract steps dicts from a list."""
    return [
        {
            "stepId": s.get("stepId"),
            "stepNumber": s.get("stepNumber"),
            "stepName": s.get("stepName"),
            "instructionText": s.get("instructionText"),
            "fields": extract_fields(s.get("fields")),
            "endpointURL": s.get("endpointURL"),
        }
        for s in steps or []
    ]

def extract_jobs(jobs: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Extract jobs dicts from a list."""
    return [
        {
            "id": j.get("id"),
            "code": j.get("code"),
            "scheduledDate": j.get("scheduledDate"),
            "finishedDate": j.get("finishedDate"),
            "scheduledDateAsText": j.get("scheduledDateAsText"),
            "finishedDateAsText": j.get("finishedDateAsText"),
            "status": j.get("status"),
            "assignedBy": j.get("assignedBy"),
            "assignedTo": j.get("assignedTo"),
            "summaryText": j.get("summaryText"),
            "miniSummaryText": j.get("miniSummaryText"),
            "jobColour": j.get("jobColour"),
            "jobNumber": j.get("jobNumber"),
            "stepText": j.get("stepText"),
            "steps": extract_steps(j.get("steps")),
            "endpointURL": j.get("endpointURL"),
            "jobVersion": j.get("jobVersion"),
            "workOrderId": j.get("workOrderId"),
            "type": j.get("type"),
            "operationType": j.get("operationType"),
        }
        for j in jobs or []
    ]

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    BASE_URL = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")

    endpoint_path = "/smwe/api/v6/workorders/list/"
    url = BASE_URL + endpoint_path

    output_dir = os.path.abspath("Main/data/GET--jobs")
    ensure_dir(output_dir)
    output_path = os.path.join(output_dir, "jobs.json")

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    session = requests.Session()
    session.headers.update(headers)

    # First fetch to get count of workorders, NO params passed
    logger.info(f"Getting total number of workorders from {url} ...")
    total_results = 0
    response = None
    try:
        response = session.get(url)
        response.raise_for_status()
        result = response.json()
        total_results = result.get("totalResultCount", 0)
    except Exception as e:
        if response is not None:
            logger.error(f"❌ API response: {response.text}")
        logger.error(f"❌ Error fetching totalResultCount: {e}")
        total_results = 0

    if total_results == 0:
        logger.info("No workorders found. Exiting.")
    else:
        batch_size = 100
        offset = 0
        all_workorders: List[Dict[str, Any]] = []

        logger.info(f"Fetching all workorders ({total_results}) from {url} with paginated params")

        while offset < total_results:
            # No params passed except pagination
            params = {
                "first": offset,
                "max": batch_size,
            }
            logger.info(f"Requesting offset {offset}")
            response = None
            try:
                response = session.get(url, params=params)
                response.raise_for_status()
                result = response.json()

                workorders = result.get("workOrders", [])
                if workorders is None or not workorders:
                    logger.info("No more workorders returned, stopping pagination.")
                    break

                for wo in workorders:
                    wo_out = {
                        "id": wo.get("id"),
                        "code": wo.get("code"),
                        "jobCount": wo.get("jobCount"),
                        "jobCountText": wo.get("jobCountText"),
                        "status": wo.get("status"),
                        "assignedTo": wo.get("assignedTo"),
                        "assignedBy": wo.get("assignedBy"),
                        "assignedDate": wo.get("assignedDate"),
                        "scheduledDate": wo.get("scheduledDate"),
                        "assignedDateAsText": wo.get("assignedDateAsText"),
                        "scheduledDateAsText": wo.get("scheduledDateAsText"),
                        "canAssign": wo.get("canAssign"),
                        "summary": wo.get("summary"),
                        "indicators": wo.get("indicators"),
                        "bond": wo.get("bond"),
                        "winery": wo.get("winery"),
                        "jobs": extract_jobs(wo.get("jobs")),
                        "colourCode": wo.get("colourCode"),
                        "endpointURL": wo.get("endpointURL"),
                    }
                    all_workorders.append(wo_out)
                logger.info(f"Retrieved {len(workorders)} workorders at offset {offset}")

                offset += batch_size

            except Exception as e:
                if response is not None:
                    logger.error(f"❌ API response: {response.text}")
                logger.error(f"❌ Error fetching workorders at offset {offset}: {e}")
                break

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_workorders, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(all_workorders)} workorders to {output_path}")