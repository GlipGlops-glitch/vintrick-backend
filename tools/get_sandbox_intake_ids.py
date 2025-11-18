# python tools/get_sandbox_intake_ids.py

import os
import json
import csv
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

if __name__ == "__main__":
    load_dotenv()
    VINTRACE_API_TOKEN = os.getenv("VINTRACE_API_TOKEN")
    
    BASE_URL = "https://sandbox.vintrace.net"
    endpoint_path = "/smwedemo/api/v6/intake-operations/search"
    url = BASE_URL + endpoint_path

    headers = {}
    if VINTRACE_API_TOKEN:
        headers["Authorization"] = f"Bearer {VINTRACE_API_TOKEN}"

    # Fetch fruit intakes
    params = {
        "maxResults": 100,
        "firstResult": 0,
        "vintage": 2025
    }
    
    logger.info(f"Fetching fruit intakes from SANDBOX...")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        fruit_intakes = result.get("intakes", [])
        
        if not fruit_intakes:
            logger.warning("⚠️ No fruit intakes found in sandbox!")
            exit(1)
        
        logger.info(f"✅ Found {len(fruit_intakes)} fruit intakes")
        
        # Display the IDs and basic info
        print("\n" + "="*80)
        print("FRUIT INTAKE IDs IN SANDBOX")
        print("="*80)
        
        intake_data = []
        for intake in fruit_intakes:
            intake_id = intake.get('id')
            docket_no = intake.get('docketNo', 'N/A')
            vintage = intake.get('vintage', 'N/A')
            variety = intake.get('variety', {}).get('name', 'N/A')
            
            # Try to get weight info
            weights = intake.get('weights', {})
            gross = weights.get('gross', {})
            tare = weights.get('tare', {})
            net = weights.get('net', {})
            
            print(f"ID: {intake_id:6} | DocketNo: {docket_no:15} | Vintage: {vintage} | Variety: {variety}")
            
            intake_data.append({
                'id': intake_id,
                'docketNo': docket_no,
                'vintage': vintage,
                'variety': variety,
                'gross.value': gross.get('value', ''),
                'gross.unit': gross.get('unit', ''),
                'tare.value': tare.get('value', ''),
                'tare.unit': tare.get('unit', ''),
                'net.value': net.get('value', ''),
                'net.unit': net.get('unit', ''),
            })
        
        print("="*80)
        
        # Save to CSV for easy reference
        csv_output = "tools/sandbox_fruit_intake_ids.csv"
        with open(csv_output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'docketNo', 'vintage', 'variety', 
                         'gross.value', 'gross.unit', 'tare.value', 'tare.unit', 
                         'net.value', 'net.unit', 'unitPrice.value', 'unitPrice.unit']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for data in intake_data:
                # Add empty pricing columns
                data['unitPrice.value'] = ''
                data['unitPrice.unit'] = '$ / ton'
                writer.writerow(data)
        
        logger.info(f"✅ Saved fruit intake IDs to {csv_output}")
        logger.info(f"📝 You can now fill in the unitPrice.value column and use this file with the uploader!")
        
        # Save full JSON for reference
        json_output = "tools/sandbox_fruit_intakes_full.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(fruit_intakes, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved full JSON to {json_output}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise