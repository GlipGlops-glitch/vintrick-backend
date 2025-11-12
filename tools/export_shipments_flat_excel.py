# vintrick-backend/tools/export_shipments_powerbi_style.py
# Comment: Export shipments to Excel with only the main columns (Power BI style), not one column per every nested element.

import pandas as pd
import json
import os

# --- CONFIG ---
JSON_PATH = os.getenv("SHIPMENTS_JSON", "Main/data/GET--shipments/10_shipments.json")
EXPORT_PATH = os.getenv("EXPORT_PATH", "Tools/shipments_powerbi_style.xlsx")

def extract_flat_row(s, wine_detail, composition):
    # Shipment-level fields
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
        # Source
        "source.id": s.get("source", {}).get("id"),
        "source.name": s.get("source", {}).get("name"),
        "source.businessUnit": s.get("source", {}).get("businessUnit"),
        # Destination
        "destination.winery.name": s.get("destination", {}).get("winery", {}).get("name") if isinstance(s.get("destination", {}).get("winery"), dict) else None,
        "destination.party.id": s.get("destination", {}).get("party", {}).get("id") if isinstance(s.get("destination", {}).get("party"), dict) else None,
        "destination.party.name": s.get("destination", {}).get("party", {}).get("name") if isinstance(s.get("destination", {}).get("party"), dict) else None,
        # Carrier/DispatchType
        "carrier": s.get("carrier", {}).get("name") if isinstance(s.get("carrier"), dict) else s.get("carrier"),
        "dispatchType.id": s.get("dispatchType", {}).get("id") if isinstance(s.get("dispatchType"), dict) else None,
        "dispatchType.name": s.get("dispatchType", {}).get("name") if isinstance(s.get("dispatchType"), dict) else None,
    }

    # WineDetails
    row.update({
        "wineDetails.vessel": wine_detail.get("vessel"),
        "wineDetails.batch": wine_detail.get("batch"),
        "wineDetails.weight": wine_detail.get("weight"),
        "wineDetails.volume.unit": wine_detail.get("volume", {}).get("unit") if wine_detail.get("volume") else None,
        "wineDetails.volume.value": wine_detail.get("volume", {}).get("value") if wine_detail.get("volume") else None,
        "wineDetails.loss.volume.unit": wine_detail.get("loss", {}).get("volume", {}).get("unit") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("volume") else None,
        "wineDetails.loss.volume.value": wine_detail.get("loss", {}).get("volume", {}).get("value") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("volume") else None,
        "wineDetails.loss.reason.id": wine_detail.get("loss", {}).get("reason", {}).get("id") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("reason") else None,
        "wineDetails.loss.reason.name": wine_detail.get("loss", {}).get("reason", {}).get("name") if wine_detail.get("loss") and wine_detail.get("loss", {}).get("reason") else None,
        "wineDetails.bottlingDetails": wine_detail.get("bottlingDetails"),
    })

    # Winery Building
    row["wineDetails.wineryBuilding.id"] = wine_detail.get("wineryBuilding", {}).get("id") if isinstance(wine_detail.get("wineryBuilding"), dict) else None
    row["wineDetails.wineryBuilding.name"] = wine_detail.get("wineryBuilding", {}).get("name") if isinstance(wine_detail.get("wineryBuilding"), dict) else None

    # WineBatch
    wine_batch = wine_detail.get("wineBatch", {})
    row.update({
        "wineBatch.id": wine_batch.get("id"),
        "wineBatch.name": wine_batch.get("name"),
        "wineBatch.description": wine_batch.get("description"),
        "wineBatch.vintage": wine_batch.get("vintage"),
        "wineBatch.program": wine_batch.get("program"),
        # Designated Region
        "wineBatch.designatedRegion.id": wine_batch.get("designatedRegion", {}).get("id") if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
        "wineBatch.designatedRegion.name": wine_batch.get("designatedRegion", {}).get("name") if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
        "wineBatch.designatedRegion.code": wine_batch.get("designatedRegion", {}).get("code") if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
        # Designated Variety
        "wineBatch.designatedVariety.id": wine_batch.get("designatedVariety", {}).get("id") if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
        "wineBatch.designatedVariety.name": wine_batch.get("designatedVariety", {}).get("name") if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
        "wineBatch.designatedVariety.code": wine_batch.get("designatedVariety", {}).get("code") if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
        # Product Category
        "wineBatch.productCategory.id": wine_batch.get("productCategory", {}).get("id") if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
        "wineBatch.productCategory.name": wine_batch.get("productCategory", {}).get("name") if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
        "wineBatch.productCategory.code": wine_batch.get("productCategory", {}).get("code") if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
        # Designated Product
        "wineBatch.designatedProduct.id": wine_batch.get("designatedProduct", {}).get("id") if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
        "wineBatch.designatedProduct.name": wine_batch.get("designatedProduct", {}).get("name") if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
        "wineBatch.designatedProduct.code": wine_batch.get("designatedProduct", {}).get("code") if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
        # Grading
        "wineBatch.grading.scaleId": wine_batch.get("grading", {}).get("scaleId") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
        "wineBatch.grading.scaleName": wine_batch.get("grading", {}).get("scaleName") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
        "wineBatch.grading.valueId": wine_batch.get("grading", {}).get("valueId") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
        "wineBatch.grading.valueName": wine_batch.get("grading", {}).get("valueName") if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
    })

    # Cost
    cost = wine_detail.get("cost", {})
    for field in ["total", "fruit", "overhead", "storage", "additive", "bulk", "packaging", "operation", "freight", "other", "average"]:
        row[f"wineDetails.cost.{field}"] = cost.get(field)

    # Composition (one per row, PowerBI style)
    if composition:
        row.update({
            "composition.percentage": composition.get("percentage"),
            "composition.vintage": composition.get("vintage"),
            "composition.subRegion": composition.get("subRegion"),
            # Block
            "composition.block.id": composition.get("block", {}).get("id") if "block" in composition and isinstance(composition.get("block"), dict) else None,
            "composition.block.name": composition.get("block", {}).get("name") if "block" in composition and isinstance(composition.get("block"), dict) else None,
            "composition.block.extId": composition.get("block", {}).get("extId") if "block" in composition and isinstance(composition.get("block"), dict) else None,
            # Region
            "composition.region.id": composition.get("region", {}).get("id") if "region" in composition and isinstance(composition.get("region"), dict) else None,
            "composition.region.name": composition.get("region", {}).get("name") if "region" in composition and isinstance(composition.get("region"), dict) else None,
            # Variety
            "composition.variety.id": composition.get("variety", {}).get("id") if "variety" in composition and isinstance(composition.get("variety"), dict) else None,
            "composition.variety.name": composition.get("variety", {}).get("name") if "variety" in composition and isinstance(composition.get("variety"), dict) else None,
        })
    else:
        row.update({
            "composition.percentage": None,
            "composition.vintage": None,
            "composition.subRegion": None,
            "composition.block.id": None,
            "composition.block.name": None,
            "composition.block.extId": None,
            "composition.region.id": None,
            "composition.region.name": None,
            "composition.variety.id": None,
            "composition.variety.name": None,
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

# --- EXPORT TO EXCEL ---
df.to_excel(EXPORT_PATH, index=False)
print(f"Exported {len(df)} rows to Excel: {EXPORT_PATH}")

"""
How to use:
- Place your JSON file at Main/data/GET--shipments/10_shipments.json (or set SHIPMENTS_JSON env var)
- Run: python vintrick-backend/tools/export_shipments_powerbi_style.py
- Output Excel file will be at Tools/shipments_powerbi_style.xlsx (or set EXPORT_PATH env var)
- Opens in Power BI, Excel, etc. with a normalized, readable column set (not one column per every nested element).
"""