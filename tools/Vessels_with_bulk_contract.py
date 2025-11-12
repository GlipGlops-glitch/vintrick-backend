
# python tools/Vessels_with_bulk_contract.py

import os
import csv
import json
import logging
from typing import Set

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def ensure_dir(dir_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def parse_production_year(year_str: str) -> int:
    """Parse production year string to integer."""
    if not year_str or year_str.strip() == '':
        return 0
    try:
        return int(year_str.strip())
    except ValueError:
        logger.warning(f"Could not parse production year: '{year_str}'")
        return 0

def is_unspecified(weigh_tag: str) -> bool:
    """Check if weigh tag is 'Unspecified' (case-insensitive)."""
    if not weigh_tag:
        return False
    return weigh_tag.strip().lower() == 'unspecified'

def get_unspecified_vessels(csv_path: str, min_vintage: int = 2023) -> Set[str]:
    """
    Get unique vessel names with 'Unspecified' weigh tag and vintage >= min_vintage.
    
    Args:
        csv_path: Path to the CSV file
        min_vintage: Minimum vintage year (default: 2023)
    
    Returns:
        Set of unique vessel names
    """
    vessels = set()
    total_records = 0
    matching_records = 0
    
    logger.info(f"Reading CSV from: {csv_path}")
    logger.info(f"Filtering for: Weigh tag# = 'Unspecified' AND Production year >= {min_vintage}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Verify required columns exist
            if 'Weigh tag#' not in reader.fieldnames:
                logger.error("Column 'Weigh tag#' not found in CSV")
                return set()
            if 'Production year' not in reader.fieldnames:
                logger.error("Column 'Production year' not found in CSV")
                return set()
            if 'Vessel' not in reader.fieldnames:
                logger.error("Column 'Vessel' not found in CSV")
                return set()
            
            for row in reader:
                total_records += 1
                
                weigh_tag = row.get('Weigh tag#', '')
                production_year_str = row.get('Production year', '')
                vessel = row.get('Vessel', '').strip()
                
                # Parse production year
                production_year = parse_production_year(production_year_str)
                
                # Check if matches criteria
                if is_unspecified(weigh_tag) and production_year >= min_vintage and vessel:
                    vessels.add(vessel)
                    matching_records += 1
        
        logger.info(f"✅ Processed {total_records} total records")
        logger.info(f"✅ Found {matching_records} matching records")
        logger.info(f"✅ Identified {len(vessels)} unique vessels")
        
    except FileNotFoundError:
        logger.error(f"❌ File not found: {csv_path}")
        return set()
    except Exception as e:
        logger.error(f"❌ Error reading CSV: {e}")
        return set()
    
    return vessels

if __name__ == "__main__":
    # Input and output paths
    input_csv = "Main/data/vintrace_reports/Vessel_Contents_Main.csv"
    output_dir = "Main/data/vintrace_reports/analysis"
    ensure_dir(output_dir)
    
    output_json = os.path.join(output_dir, "unspecified_vessels.json")
    
    # Minimum vintage year
    MIN_VINTAGE = 2023
    
    logger.info("="*60)
    logger.info("UNSPECIFIED VESSEL IDENTIFIER")
    logger.info("="*60)
    
    # Get unique vessels
    vessels = get_unspecified_vessels(input_csv, MIN_VINTAGE)
    
    if vessels:
        # Convert set to sorted list
        vessels_list = sorted(list(vessels))
        
        # Create output structure
        output_data = {
            "vessels": vessels_list,
            "count": len(vessels_list),
            "criteria": {
                "weigh_tag": "Unspecified",
                "min_vintage": MIN_VINTAGE
            }
        }
        
        # Write to JSON
        try:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(vessels_list)} vessels to {output_json}")
        except Exception as e:
            logger.error(f"❌ Error writing JSON: {e}")
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info(f"Total unique vessels: {len(vessels_list)}")
        logger.info("="*60)
        
        # Show sample vessels
        logger.info(f"\nSample vessels (first 10):")
        for vessel in vessels_list[:10]:
            logger.info(f"  - {vessel}")
        
        if len(vessels_list) > 10:
            logger.info(f"  ... and {len(vessels_list) - 10} more")
    else:
        logger.info("No matching vessels found.")
    
    logger.info("\n" + "="*60)
    logger.info("PROCESSING COMPLETE")
    logger.info("="*60)