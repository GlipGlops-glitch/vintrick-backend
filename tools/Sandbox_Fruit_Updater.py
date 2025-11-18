# python tools/Sandbox_Fruit_Updater.py

import os
import csv
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VintracePricingUploader:
    """
    A class to upload fruit intake pricing data to Vintrace API.
    """
    
    def __init__(self):
        """Initialize the uploader by loading environment variables."""
        load_dotenv()
        self.api_token = os.getenv('VINTRACE_API_TOKEN')
        
        if not self.api_token:
            raise ValueError("VINTRACE_API_TOKEN not found in .env file")
        
        self.base_url = "https://sandbox.vintrace.net/smwedemo/api/v7/operation/fruit-intakes"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def read_csv(self, csv_file: str) -> list:
        """
        Read pricing data from CSV file.
        
        Args:
            csv_file: Path to the CSV file
            
        Returns:
            List of dictionaries containing the pricing data
        """
        data = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Validate headers - now using 'id' instead of 'docketNo'
                required_columns = {
                    'id', 'net.value', 'net.unit',
                    'gross.value', 'gross.unit',
                    'tare.value', 'tare.unit',
                    'unitPrice.value', 'unitPrice.unit'
                }
                
                # Get actual column names (filtering out empty ones)
                actual_columns = {col for col in reader.fieldnames if col and col.strip()}
                
                if not required_columns.issubset(actual_columns):
                    missing = required_columns - actual_columns
                    raise ValueError(f"Missing required columns: {missing}")
                
                for row_num, row in enumerate(reader, 2):  # Start at 2 (header is row 1)
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Check if id exists
                    if not row.get('id', '').strip():
                        logger.warning(f"Row {row_num}: Missing id, skipping...")
                        continue
                    
                    data.append(row)
                    
            logger.info(f"Successfully read {len(data)} rows from {csv_file}")
            return data
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_file}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def prepare_payload(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Transform CSV row data into API payload format.
        
        Args:
            row: Dictionary containing CSV row data
            
        Returns:
            Formatted payload for API request, or None if data is invalid
        """
        try:
            # Helper function to safely convert to float
            def safe_float(value):
                if value is None or str(value).strip() == '':
                    return None
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            
            # Helper function to get non-empty string
            def safe_string(value):
                return value.strip() if value and str(value).strip() else None
            
            payload = {
                "data": {
                    "gross": {
                        "value": safe_float(row.get('gross.value')),
                        "unit": safe_string(row.get('gross.unit'))
                    },
                    "tare": {
                        "value": safe_float(row.get('tare.value')),
                        "unit": safe_string(row.get('tare.unit'))
                    },
                    "net": {
                        "value": safe_float(row.get('net.value')),
                        "unit": safe_string(row.get('net.unit'))
                    },
                    "unitPrice": {
                        "value": safe_float(row.get('unitPrice.value')),
                        "unit": safe_string(row.get('unitPrice.unit'))
                    }
                }
            }
            
            # Validate that we have required data
            if payload['data']['unitPrice']['value'] == 0 or payload['data']['unitPrice']['value'] is None:
                logger.warning(f"Warning: unitPrice is 0 or missing for id {row.get('id')}")
            
            return payload
            
        except Exception as e:
            logger.error(f"Error preparing payload: {e}")
            return None
    
    def post_pricing(self, fruit_intake_id: str, payload: Dict[str, Any]) -> bool:
        """
        Post pricing data to Vintrace API.
        
        Args:
            fruit_intake_id: The fruit intake ID
            payload: The pricing data payload
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/{fruit_intake_id}/pricing"
        
        try:
            logger.debug(f"Posting to URL: {url}")
            logger.debug(f"Payload: {payload}")
            
            response = requests.put(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"✓ Successfully posted pricing for intake ID: {fruit_intake_id}")
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ HTTP error for intake ID {fruit_intake_id}: {e}")
            logger.error(f"  Status Code: {response.status_code}")
            logger.error(f"  Response: {response.text}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Request error for intake ID {fruit_intake_id}: {e}")
            return False
    
    def upload_from_csv(self, csv_file: str, skip_if_zero_price: bool = True) -> Dict[str, int]:
        """
        Read CSV and upload all pricing data to Vintrace API.
        
        Args:
            csv_file: Path to the CSV file
            skip_if_zero_price: Skip rows where unitPrice is 0 or empty
            
        Returns:
            Dictionary with success, failed, and skipped counts
        """
        data = self.read_csv(csv_file)
        results = {'success': 0, 'failed': 0, 'skipped': 0}
        
        logger.info(f"Starting upload of {len(data)} records...")
        
        for idx, row in enumerate(data, 1):
            fruit_intake_id = row['id'].strip()
            
            if not fruit_intake_id:
                logger.warning(f"Row {idx}: Missing id, skipping...")
                results['skipped'] += 1
                continue
            
            # Check if we should skip due to zero price
            unit_price = row.get('unitPrice.value', '').strip()
            if skip_if_zero_price and (not unit_price or float(unit_price) == 0):
                logger.warning(f"Row {idx}: Skipping intake ID {fruit_intake_id} - unitPrice is 0 or empty")
                results['skipped'] += 1
                continue
            
            payload = self.prepare_payload(row)
            
            if payload is None:
                logger.error(f"Row {idx}: Failed to prepare payload for intake ID {fruit_intake_id}")
                results['failed'] += 1
                continue
            
            logger.info(f"Processing {idx}/{len(data)}: intake ID {fruit_intake_id}")
            
            if self.post_pricing(fruit_intake_id, payload):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        logger.info("\n" + "="*50)
        logger.info(f"Upload complete!")
        logger.info(f"Successful: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Skipped: {results['skipped']}")
        logger.info("="*50)
        
        return results


def main():
    """Main function to run the uploader."""
    # Specify your CSV file path here
    csv_file = 'tools/sandbox_fruit_intake_ids.csv'
    
    # Set to False if you want to upload even when unitPrice is 0
    skip_zero_price = True
    
    try:
        uploader = VintracePricingUploader()
        results = uploader.upload_from_csv(csv_file, skip_if_zero_price=skip_zero_price)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()