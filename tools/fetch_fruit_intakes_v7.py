# python tools/Fetch_Fruit_Intakes.py

import os
import json
import csv
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VintraceFruitIntakeFetcher:
    """
    A class to fetch fruit intake data from Vintrace API.
    """
    
    def __init__(self):
        """Initialize the fetcher by loading environment variables."""
        load_dotenv()
        self.api_token = os.getenv('VINTRACE_API_TOKEN')
        
        if not self.api_token:
            raise ValueError("VINTRACE_API_TOKEN not found in .env file")
        
        self.base_url = "https://sandbox.vintrace.net/smwedemo/api/v7/operation/fruit-intakes"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_fruit_intakes(self, params: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all fruit intakes from Vintrace API.
        
        Args:
            params: Optional query parameters for filtering (e.g., date range, status)
            
        Returns:
            List of fruit intake records, or None if request fails
        """
        try:
            logger.info(f"📥 Fetching fruit intakes from: {self.base_url}")
            
            if params:
                logger.info(f"🔍 Query parameters: {json.dumps(params, indent=2)}")
            
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response structures
            if isinstance(data, dict):
                # If response has a 'data' field
                if 'data' in data:
                    intakes = data['data']
                # If response has 'items' field
                elif 'items' in data:
                    intakes = data['items']
                # If it's wrapped differently
                else:
                    intakes = [data]
            elif isinstance(data, list):
                intakes = data
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                intakes = []
            
            logger.info(f"✓ Successfully fetched {len(intakes)} fruit intake records")
            return intakes
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ HTTP error fetching fruit intakes: {e}")
            logger.error(f"  Status Code: {response.status_code}")
            logger.error(f"  Response: {response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Request error fetching fruit intakes: {e}")
            return None
        
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return None
    
    def get_fruit_intake_by_id(self, intake_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific fruit intake by ID.
        
        Args:
            intake_id: The fruit intake ID (docket number)
            
        Returns:
            Fruit intake record, or None if request fails
        """
        url = f"{self.base_url}/{intake_id}"
        
        try:
            logger.info(f"📥 Fetching fruit intake: {intake_id}")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"✓ Successfully fetched fruit intake {intake_id}")
            return data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ HTTP error fetching intake {intake_id}: {e}")
            logger.error(f"  Status Code: {response.status_code}")
            logger.error(f"  Response: {response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Request error fetching intake {intake_id}: {e}")
            return None
    
    def save_to_json(self, intakes: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save fruit intakes to a JSON file.
        
        Args:
            intakes: List of fruit intake records
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'tools/fruit_intakes_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(intakes, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved {len(intakes)} records to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"✗ Error saving to JSON: {e}")
            raise
    
    def save_to_csv(self, intakes: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Save fruit intakes to a CSV file.
        Extracts key fields including pricing data.
        
        Args:
            intakes: List of fruit intake records
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'tools/fruit_intakes_{timestamp}.csv'
        
        if not intakes:
            logger.warning("No intakes to save to CSV")
            return None
        
        try:
            # Define CSV columns
            fieldnames = [
                'id',
                'docketNo',
                'date',
                'gross.value',
                'gross.unit',
                'tare.value',
                'tare.unit',
                'net.value',
                'net.unit',
                'unitPrice.value',
                'unitPrice.unit',
                'block',
                'vineyard',
                'variety'
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for intake in intakes:
                    # Extract nested fields safely
                    row = {
                        'id': intake.get('id', ''),
                        'docketNo': intake.get('docketNo', ''),
                        'date': intake.get('date', ''),
                        'gross.value': intake.get('gross', {}).get('value', ''),
                        'gross.unit': intake.get('gross', {}).get('unit', ''),
                        'tare.value': intake.get('tare', {}).get('value', ''),
                        'tare.unit': intake.get('tare', {}).get('unit', ''),
                        'net.value': intake.get('net', {}).get('value', ''),
                        'net.unit': intake.get('net', {}).get('unit', ''),
                        'unitPrice.value': intake.get('unitPrice', {}).get('value', ''),
                        'unitPrice.unit': intake.get('unitPrice', {}).get('unit', ''),
                        'block': intake.get('block', {}).get('name', ''),
                        'vineyard': intake.get('vineyard', {}).get('name', ''),
                        'variety': intake.get('variety', {}).get('name', '')
                    }
                    writer.writerow(row)
            
            logger.info(f"💾 Saved {len(intakes)} records to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"✗ Error saving to CSV: {e}")
            raise
    
    def display_summary(self, intakes: List[Dict[str, Any]]) -> None:
        """
        Display a summary of the fetched fruit intakes.
        
        Args:
            intakes: List of fruit intake records
        """
        if not intakes:
            logger.warning("No intakes to display")
            return
        
        logger.info("\n" + "="*70)
        logger.info(f"FRUIT INTAKE SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Records: {len(intakes)}")
        logger.info("="*70)
        
        for idx, intake in enumerate(intakes, 1):
            intake_id = intake.get('id', 'N/A')
            docket_no = intake.get('docketNo', 'N/A')
            date = intake.get('date', 'N/A')
            
            # Get weight info
            net = intake.get('net', {})
            net_value = net.get('value', 'N/A')
            net_unit = net.get('unit', '')
            
            # Get pricing info
            unit_price = intake.get('unitPrice', {})
            price_value = unit_price.get('value', 'N/A')
            price_unit = unit_price.get('unit', '')
            
            # Get vineyard info
            block = intake.get('block', {}).get('name', 'N/A')
            vineyard = intake.get('vineyard', {}).get('name', 'N/A')
            variety = intake.get('variety', {}).get('name', 'N/A')
            
            logger.info(f"\n{idx}. Docket: {docket_no} (ID: {intake_id})")
            logger.info(f"   Date: {date}")
            logger.info(f"   Vineyard: {vineyard} | Block: {block} | Variety: {variety}")
            logger.info(f"   Net Weight: {net_value} {net_unit}")
            logger.info(f"   Unit Price: {price_value} {price_unit}")
        
        logger.info("\n" + "="*70)


def main():
    """Main function to fetch and display fruit intakes."""
    
    try:
        fetcher = VintraceFruitIntakeFetcher()
        
        # Fetch all fruit intakes
        intakes = fetcher.get_fruit_intakes()
        
        if intakes is None:
            logger.error("Failed to fetch fruit intakes")
            return
        
        if not intakes:
            logger.warning("No fruit intakes found")
            return
        
        # Display summary
        fetcher.display_summary(intakes)
        
        # Save to JSON
        json_file = fetcher.save_to_json(intakes)
        
        # Save to CSV
        csv_file = fetcher.save_to_csv(intakes)
        
        logger.info(f"\n✅ Fetch complete!")
        logger.info(f"📄 JSON file: {json_file}")
        logger.info(f"📊 CSV file: {csv_file}")
        
        # Example: Fetch a specific intake by ID
        # if intakes:
        #     first_id = intakes[0].get('id')
        #     if first_id:
        #         specific_intake = fetcher.get_fruit_intake_by_id(first_id)
        #         logger.info(f"\n📋 Specific intake:\n{json.dumps(specific_intake, indent=2)}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()