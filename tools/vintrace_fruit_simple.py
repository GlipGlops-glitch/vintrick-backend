#python tools/vintrace_fruit_simple.py

import json
import os

# Input and output file paths
input_path = "Main/data/GET--fruit_intakes/tables/fr_fruit_intakes.json"
output_path = "Main/data/GET--fruit_intakes/tables/fr_fruit_intakes_extracted.json"

def extract_fields(input_file, output_file):
    # Read the input JSON file
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract the required fields for each entry
    extracted = []
    for entry in data:
        extracted.append({
            "fr_docketNo": entry.get("fr_docketNo"),
            "fr_amount_value": entry.get("fr_amount_value"),
            "fr_fruitCost": entry.get("fr_fruitCost"),
        })

    # Write the extracted data to the output JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2)

if __name__ == "__main__":
    extract_fields(input_path, output_path)
    print(f"Extracted fields saved to {output_path}")