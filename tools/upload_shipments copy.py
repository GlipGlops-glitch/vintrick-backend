# vintrick-backend/tools/upload_shipments_powerbi_style.py
# Comment: Upload PowerBI-style flattened shipments JSON directly to SQL Server, skipping Excel.

import pandas as pd
import json
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
JSON_PATH = os.getenv("SHIPMENTS_JSON", "Main/data/GET--shipments/all_shipments.json")
DATABASE_URL = os.getenv("DB_URL")
TABLE_NAME = os.getenv("SHIPMENTS_TABLE", "shipments_vintrace")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Please add to .env or environment.")

def extract_flat_row(s, wine_detail, composition):
    row = {
        "id": s.get("id"),
        "workOrderNumber": s.get("workOrderNumber"),
        "jobNumber": s.get("jobNumber"),
        "shipmentNumber": s.get("shipmentNumber"),
        "type": s.get("type"),
        "occurredTime": s.get("occurredTime"),
        "modifiedTime": s.get("modifiedTime"),
        "reference": s.get("reference"),
        "freightCode": s.get("freightCode"),
        "reversed": s.get("reversed"),
        "source_id": s.get("source", {}).get("id"),
        "source_name": s.get("source", {}).get("name"),
        "source_businessUnit": s.get("source", {}).get("businessUnit"),
        "destination_winery_name": s.get("destination", {}).get("winery", {}).get("name") if isinstance(s.get("destination", {}).get("winery"), dict) else None,
        "destination_party_id": s.get("destination", {}).get("party", {}).get("id") if isinstance(s.get("destination", {}).get("party"), dict) else None,
        "destination_party_name": s.get("destination", {}).get("party", {}).get("name") if isinstance(s.get("destination", {}).get("party"), dict) else None,
        "carrier": s.get("carrier", {}).get("name") if isinstance(s.get("carrier"), dict) else s.get("carrier"),
        "dispatchType_id": s.get("dispatchType", {}).get("id") if isinstance(s.get("dispatchType"), dict) else None,
        "dispatchType_name": s.get("dispatchType", {}).get("name") if isinstance(s.get("dispatchType"), dict) else None,
        "wineDetails_vessel": wine_detail.get("vessel"),
        "wineDetails_batch": wine_detail.get("batch"),
        "wineDetails_weight": wine_detail.get("weight"),
        "wineDetails_volume_unit": wine_detail.get("volume", {}).get("unit") if wine_detail.get("volume") else None,
        "wineDetails_volume_value": wine_detail.get("volume", {}).get("value") if wine_detail.get("volume") else None,
        "wineDetails_loss_volume_unit": wine_detail.get("loss", {}).get("volume", {}).get("unit") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("volume") else None,
        "wineDetails_loss_volume_value": wine_detail.get("loss", {}).get("volume", {}).get("value") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("volume") else None,
        "wineDetails_loss_reason_id": wine_detail.get("loss", {}).get("reason", {}).get("id") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("reason") else None,
        "wineDetails_loss_reason_name": wine_detail.get("loss", {}).get("reason", {}).get("name") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("reason") else None,
        "wineDetails_bottlingDetails": wine_detail.get("bottlingDetails"),
        "wineDetails_wineryBuilding_id": wine_detail.get("wineryBuilding", {}).get("id") if isinstance(wine_detail.get("wineryBuilding"), dict) else None,
        "wineDetails_wineryBuilding_name": wine_detail.get("wineryBuilding", {}).get("name") if isinstance(wine_detail.get("wineryBuilding"), dict) else None,
    }
    wine_batch = wine_detail.get("wineBatch", {})
    row.update({
        "wineBatch_id": wine_batch.get("id"),
        "wineBatch_name": wine_batch.get("name"),
        "wineBatch_description": wine_batch.get("description"),
        "wineBatch_vintage": wine_batch.get("vintage"),
        "wineBatch_program": wine_batch.get("program"),
        "wineBatch_designatedRegion_id": wine_batch.get("designatedRegion", {}).get("id") if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
        "wineBatch_designatedRegion_name": wine_batch.get("designatedRegion", {}).get("name") if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
        "wineBatch_designatedRegion_code": wine_batch.get("designatedRegion", {}).get("code") if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
        "wineBatch_designatedVariety_id": wine_batch.get("designatedVariety", {}).get("id") if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
        "wineBatch_designatedVariety_name": wine_batch.get("designatedVariety", {}).get("name") if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
        "wineBatch_designatedVariety_code": wine_batch.get("designatedVariety", {}).get("code") if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
        "wineBatch_productCategory_id": wine_batch.get("productCategory", {}).get("id") if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
        "wineBatch_productCategory_name": wine_batch.get("productCategory", {}).get("name") if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
        "wineBatch_productCategory_code": wine_batch.get("productCategory", {}).get("code") if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
        "wineBatch_designatedProduct_id": wine_batch.get("designatedProduct", {}).get("id") if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
        "wineBatch_designatedProduct_name": wine_batch.get("designatedProduct", {}).get("name") if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
        "wineBatch_designatedProduct_code": wine_batch.get("designatedProduct", {}).get("code") if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
        "wineBatch_grading_scaleId": wine_batch.get("grading", {}).get("scaleId") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
        "wineBatch_grading_scaleName": wine_batch.get("grading", {}).get("scaleName") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
        "wineBatch_grading_valueId": wine_batch.get("grading", {}).get("valueId") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
        "wineBatch_grading_valueName": wine_batch.get("grading", {}).get("valueName") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
    })
    cost = wine_detail.get("cost", {})
    for field in ["total", "fruit", "overhead", "storage", "additive", "bulk", "packaging", "operation", "freight", "other", "average"]:
        row[f"wineDetails_cost_{field}"] = cost.get(field)
    if composition:
        row.update({
            "composition_percentage": composition.get("percentage"),
            "composition_vintage": composition.get("vintage"),
            "composition_subRegion": composition.get("subRegion"),
            "composition_block_id": composition.get("block", {}).get("id") if "block" in composition and isinstance(composition.get("block"), dict) else None,
            "composition_block_name": composition.get("block", {}).get("name") if "block" in composition and isinstance(composition.get("block"), dict) else None,
            "composition_block_extId": composition.get("block", {}).get("extId") if "block" in composition and isinstance(composition.get("block"), dict) else None,
            "composition_region_id": composition.get("region", {}).get("id") if "region" in composition and isinstance(composition.get("region"), dict) else None,
            "composition_region_name": composition.get("region", {}).get("name") if "region" in composition and isinstance(composition.get("region"), dict) else None,
            "composition_variety_id": composition.get("variety", {}).get("id") if "variety" in composition and isinstance(composition.get("variety"), dict) else None,
            "composition_variety_name": composition.get("variety", {}).get("name") if "variety" in composition and isinstance(composition.get("variety"), dict) else None,
        })
    else:
        row.update({
            "composition_percentage": None,
            "composition_vintage": None,
            "composition_subRegion": None,
            "composition_block_id": None,
            "composition_block_name": None,
            "composition_block_extId": None,
            "composition_region_id": None,
            "composition_region_name": None,
            "composition_variety_id": None,
            "composition_variety_name": None,
        })
    return row

# --- LOAD AND FLATTEN ---
with open(JSON_PATH, "r", encoding="utf-8") as f:
    shipments = json.load(f)

flat_rows = []
for s in shipments:
    wine_details = s.get("wineDetails", [])
    for wine_detail in wine_details:
        compositions = wine_detail.get("composition", [])
        if compositions:
            for composition in compositions:
                flat_rows.append(extract_flat_row(s, wine_detail, composition))
        else:
            flat_rows.append(extract_flat_row(s, wine_detail, None))

df = pd.DataFrame(flat_rows)

# --- CLEAN COLUMN NAMES FOR SQL ---
df.columns = [str(c).replace(' ', '_').replace('-', '_').replace('.', '__') for c in df.columns]

# --- UPLOAD TO SQL SERVER ---
engine = create_engine(DATABASE_URL)

def safe_to_sql(df, table_name, engine):
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Uploaded {len(df)} rows to table '{table_name}'")
    except Exception as e:
        print("Upload failed:", e)
        print("DataFrame columns:", df.columns.tolist())
        print("Sample row:", df.iloc[0].to_dict())
        raise

safe_to_sql(df, TABLE_NAME, engine)

print("All done!")

"""
How to use:
1. Set SHIPMENTS_JSON and DATABASE_URL in your environment (.env) or edit above.
2. Run: python vintrick-backend/tools/upload_shipments_powerbi_style.py
3. Data will upload to the SQL table (auto-creates columns if needed).
"""