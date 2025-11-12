
# python tools/fetch_barrels.py

import os
import json
import logging
from dotenv import load_dotenv
import requests
import pandas as pd

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

def get_env():
    load_dotenv()
    api_token = os.getenv("VINTRACE_API_TOKEN")
    base_url = os.getenv("BASE_VINTRACE_URL", "https://us61.vintrace.net")
    if not api_token:
        logger.error("No VINTRACE_API_TOKEN found in environment. Exiting.")
        exit(1)
    return api_token, base_url

def fetch_total_results(url, headers):
    params = {
        "limit": 1,
        "offset": 0,
        "extraFields": "allocations"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        return result.get("totalResults", 0)
    except Exception as e:
        logger.error(f"❌ Error fetching totalResults: {e}")
        return 0

def fetch_all_vessels(url, headers, total_results):
    limit = 200
    offset = 0
    all_vessels = []
    while offset < total_results:
        params = {
            "extraFields": "allocations,composition",
            "limit": limit,
            "offset": offset
        }
        logger.info(f"Requesting offset {offset}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            vessels = result.get("results", [])
            if not vessels:
                logger.info("No more vessels returned, stopping pagination.")
                break
            all_vessels.extend(vessels)
            logger.info(f"Retrieved {len(vessels)} vessels at offset {offset}")
            offset += limit
        except Exception as e:
            logger.error(f"❌ Error fetching vessels at offset {offset}: {e}")
            break
    return all_vessels

def fetch_barrel_group_details(base_url, headers, barrel_ids):
    details = []
    for idx, barrel_id in enumerate(barrel_ids):
        endpoint = f"/smwe/api/v7/vessel/barrel-groups/{barrel_id}"
        url = base_url + endpoint
        logger.info(f"Fetching barrel group details for id {barrel_id} ({idx+1}/{len(barrel_ids)})")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            details.append(data)
        except Exception as e:
            logger.error(f"❌ Error fetching barrel group {barrel_id}: {e}")
    return details

if __name__ == "__main__":
    api_token, base_url = get_env()
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    vessel_endpoint = "/smwe/api/v7/report/vessel-details-report"
    vessel_url = base_url + vessel_endpoint

    output_dir = "Main/data/GET--vessels"
    ensure_dir(output_dir)

    # 1. Fetch total results to paginate through all vessels
    total_results = fetch_total_results(vessel_url, headers)
    logger.info(f"Total vessels: {total_results}")

    # 2. Fetch all vessels
    all_vessels = fetch_all_vessels(vessel_url, headers, total_results)

    # 3. Get all barrel group IDs (mimicking your legacy code)
    df_all = pd.DataFrame(all_vessels)
    barrel_df = df_all[df_all['vesselType'] == 'BARREL_GROUP'] if 'vesselType' in df_all.columns else pd.DataFrame()
    barrel_df2 = pd.DataFrame(barrel_df['id']) if 'id' in barrel_df.columns else pd.DataFrame()
    barrel_ids = barrel_df2['id'].tolist() if 'id' in barrel_df2.columns else []

    logger.info(f"Found {len(barrel_ids)} barrel groups.")

    # 4. Fetch barrel group details for each barrel group ID
    barrel_details = fetch_barrel_group_details(base_url, headers, barrel_ids)

    # 5. Save only the barrel group details to json
    with open(os.path.join(output_dir, "CurrentBarrels.json"), "w") as f:
        json.dump(barrel_details, f, indent=2)
    logger.info("✅ Saved barrel group details to CurrentBarrels.json.")