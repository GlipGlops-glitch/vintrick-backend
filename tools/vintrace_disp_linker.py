# python tools/vintrace_disp_linker.py

import os
import csv
import json
import chardet

COMPOSITION_KEYS = [
    "Grower",
    "Vineyard",
    "Block",
    "Weigh tag#",
    "Delivery date",
    "Comp. %",
    "Composition volume (gal)"
]

GROUP_KEYS_ALL = ["Vessel", "Batch Code"]

def extract_index_info_from_filename(filename):
    info = {"file": filename}
    parts = filename.replace(".csv", "").split("_")
    if len(parts) >= 5 and parts[0] == "vessel" and parts[1] == "contents":
        info["date"] = parts[2].replace("-", "/")
        info["vessel"] = parts[3]
        info["batchcode"] = parts[4]
    return info

def build_index_from_csvs(csv_dir, json_index_path):
    index = []
    for fname in os.listdir(csv_dir):
        if fname.lower().endswith(".csv"):
            entry = extract_index_info_from_filename(fname)
            index.append(entry)
    with open(json_index_path, "w", encoding="utf-8") as jf:
        json.dump(index, jf, indent=2)
    print(f"[INDEX] Indexed {len(index)} CSV files in {csv_dir}.")
    return index

def read_json_index(json_index_path, csv_dir):
    if not os.path.exists(json_index_path) or os.path.getsize(json_index_path) == 0:
        print("[INDEX] No existing report_index.json, generating from CSV files...")
        return build_index_from_csvs(csv_dir, json_index_path)
    with open(json_index_path, 'r', encoding='utf-8') as jf:
        index = json.load(jf)
        if not index:
            print("[INDEX] Existing report_index.json is empty, generating from CSV files...")
            return build_index_from_csvs(csv_dir, json_index_path)
        return index

def detect_encoding(file_path, sample_size=4096):
    with open(file_path, 'rb') as f:
        raw = f.read(sample_size)
    result = chardet.detect(raw)
    encoding = result['encoding']
    print(f"[INFO] Detected encoding for {os.path.basename(file_path)}: {encoding}")
    return encoding if encoding else "utf-8"

def read_csv_file(csv_path):
    encoding = detect_encoding(csv_path)
    with open(csv_path, 'r', encoding=encoding, errors='replace') as cf:
        reader = csv.DictReader(cf)
        return [row for row in reader]

def load_work_detailz(work_detailz_path):
    if not os.path.exists(work_detailz_path):
        print(f"[WARN] work_detailz file not found: {work_detailz_path}")
        return []
    with open(work_detailz_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_fruit_intakes_extracted(fruit_intakes_path):
    if not os.path.exists(fruit_intakes_path):
        print(f"[WARN] fruit_intakes_extracted file not found: {fruit_intakes_path}")
        return []
    with open(fruit_intakes_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_lookup_dicts(work_detailz, fruit_intakes_extracted):
    work_detailz_dict = {wd.get("Delivery"): wd.get("Intake") for wd in work_detailz if wd.get("Delivery")}
    fruit_intakes_dict = {fi.get("fr_docketNo"): fi for fi in fruit_intakes_extracted if fi.get("fr_docketNo")}
    return work_detailz_dict, fruit_intakes_dict

def compact_json_entry(entry, work_detailz_dict, fruit_intakes_dict):
    csv_data = entry['csv_data']
    json_meta = entry.get("json_meta") or {}
    quantity = json_meta.get("Quantity")
    if quantity is None and isinstance(json_meta.get("original_csv"), dict):
        quantity = json_meta["original_csv"].get("Quantity")
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        quantity = None

    if not csv_data:
        return {
            "file": entry["file"],
            "meta": {},
            "composition": [],
            "json_meta": json_meta
        }
    meta = {k: v for k, v in csv_data[0].items() if k not in COMPOSITION_KEYS}
    composition = []
    for row in csv_data:
        comp_row = {k: row.get(k, "") for k in COMPOSITION_KEYS}
        try:
            comp_percent_val = float(comp_row.get("Comp. %", "0") or 0)
        except (TypeError, ValueError):
            comp_percent_val = 0
        try:
            comp_volume_val = float(comp_row.get("Composition volume (gal)", "0") or 0)
        except (TypeError, ValueError):
            comp_volume_val = 0

        weigh_tag = comp_row.get("Weigh tag#", "")
        delivery = weigh_tag if weigh_tag else ""
        intake = work_detailz_dict.get(delivery, "") or comp_row.get("Intake", "")
        comp_row["Delivery"] = delivery
        comp_row["Intake"] = intake

        fi = fruit_intakes_dict.get(intake)
        # Refactor: calculate tons based on fr_amount_unit
        tons = None
        if fi:
            amount_value = fi.get("fr_amount_value")
            amount_unit = fi.get("fr_amount_unit")
            if amount_value is not None and amount_unit:
                if amount_unit.lower() == "tn":  # tons
                    tons = amount_value
                elif amount_unit.lower() == "lb":  # pounds
                    tons = amount_value / 2000.0
        comp_row["tons"] = tons
        comp_row["fruit_cost"] = fi.get("fr_fruitCost") if fi else None

        if quantity and comp_percent_val:
            comp_row["relative_disp_gallons"] = (comp_percent_val / 100.0) * quantity
        elif comp_volume_val:
            comp_row["relative_disp_gallons"] = comp_volume_val
        else:
            comp_row["relative_disp_gallons"] = None

        composition.append(comp_row)
    return {
        "file": entry["file"],
        "meta": meta,
        "composition": composition,
        "json_meta": json_meta
    }

def process_vessel_contents_all(csv_path, work_detailz_dict, fruit_intakes_dict):
    rows = read_csv_file(csv_path)
    groups = {}
    for row in rows:
        key = tuple(row.get(k, "") for k in GROUP_KEYS_ALL)
        groups.setdefault(key, []).append(row)
    output = []
    for key, group_rows in groups.items():
        meta = {k: group_rows[0].get(k, "") for k in group_rows[0] if k not in COMPOSITION_KEYS}
        composition = []
        for row in group_rows:
            comp_row = {k: row.get(k, "") for k in COMPOSITION_KEYS}
            try:
                comp_percent_val = float(comp_row.get("Comp. %", "0") or 0)
            except (TypeError, ValueError):
                comp_percent_val = 0
            try:
                comp_volume_val = float(comp_row.get("Composition volume (gal)", "0") or 0)
            except (TypeError, ValueError):
                comp_volume_val = 0

            weigh_tag = comp_row.get("Weigh tag#", "")
            delivery = weigh_tag if weigh_tag else ""
            intake = work_detailz_dict.get(delivery, "") or comp_row.get("Intake", "")
            comp_row["Delivery"] = delivery
            comp_row["Intake"] = intake

            fi = fruit_intakes_dict.get(intake)
            # Refactor: calculate tons based on fr_amount_unit
            tons = None
            if fi:
                amount_value = fi.get("fr_amount_value")
                amount_unit = fi.get("fr_amount_unit")
                if amount_value is not None and amount_unit:
                    if amount_unit.lower() == "tn":
                        tons = amount_value
                    elif amount_unit.lower() == "lb":
                        tons = amount_value / 2000.0
            comp_row["tons"] = tons
            comp_row["fruit_cost"] = fi.get("fr_fruitCost") if fi else None

            quantity = None
            if "Quantity" in row:
                try:
                    quantity = float(row["Quantity"])
                except (TypeError, ValueError):
                    quantity = None
            if quantity and comp_percent_val:
                comp_row["relative_disp_gallons"] = (comp_percent_val / 100.0) * quantity
            elif comp_volume_val:
                comp_row["relative_disp_gallons"] = comp_volume_val
            else:
                comp_row["relative_disp_gallons"] = None
            composition.append(comp_row)
        output.append({
            "file": "vessel_contents_all.csv",
            "meta": meta,
            "composition": composition,
            "json_meta": None
        })
    return output

def build_weigh_tag_totals(compact_data):
    weigh_tag_totals = {}
    composition_meta_pairs = []
    for entry in compact_data:
        compositions = entry.get("composition")
        if compositions:
            for comp in compositions:
                composition_meta_pairs.append((comp, entry.get('json_meta')))
    for comp, json_meta in composition_meta_pairs:
        weigh_tag = comp.get("Weigh tag#", "")
        val = comp.get("relative_disp_gallons")
        dispatch_type = None
        if json_meta:
            original_csv = json_meta.get("original_csv", {})
            dispatch_type = original_csv.get("Dispatch type")
        if weigh_tag and val is not None:
            if dispatch_type != "Transferred in bond":
                weigh_tag_totals[weigh_tag] = weigh_tag_totals.get(weigh_tag, 0) + val
    for comp, json_meta in composition_meta_pairs:
        weigh_tag = comp.get("Weigh tag#", "")
        comp["total_relative_disp_gallons_other_comps_for_weigh_tag#"] = weigh_tag_totals.get(weigh_tag, 0)
    return weigh_tag_totals

def assign_relative_disp_gallons_frac(compact_data):
    all_compositions = []
    for entry in compact_data:
        compositions = entry.get("composition")
        if compositions:
            all_compositions.extend(compositions)
    intake_totals = {}
    for comp in all_compositions:
        intake = comp.get("Intake")
        val = comp.get("relative_disp_gallons")
        if intake and val is not None:
            intake_totals[intake] = intake_totals.get(intake, 0) + val
    for comp in all_compositions:
        intake = comp.get("Intake")
        val = comp.get("relative_disp_gallons")
        total = intake_totals.get(intake)
        if intake and val is not None and total and total > 0:
            comp["relative_disp_gallons_frac"] = val / total
        else:
            comp["relative_disp_gallons_frac"] = None

def merge_json_with_csv(json_index, csv_dir, work_detailz_dict, fruit_intakes_dict):
    merged = []
    zero_record_files = []
    vessel_contents_all_in_index = False
    for entry in json_index:
        csv_file = entry.get('file')
        vessel = entry.get('vessel')
        batchcode = entry.get('batchcode')
        csv_path = os.path.join(csv_dir, csv_file)
        csv_data = []
        if csv_file == "vessel_contents_all.csv":
            vessel_contents_all_in_index = True
            if os.path.exists(csv_path):
                processed_groups = process_vessel_contents_all(csv_path, work_detailz_dict, fruit_intakes_dict)
                merged.extend(processed_groups)
                print(f"[OK] Processed vessel_contents_all.csv into {len(processed_groups)} groups")
            else:
                print("[WARN] vessel_contents_all.csv not found")
            continue
        if os.path.exists(csv_path):
            try:
                all_rows = read_csv_file(csv_path)
                filtered_rows = [
                    row for row in all_rows
                    if row.get('Vessel') == vessel and (
                        row.get('Batch Code') == batchcode or row.get('Batch code') == batchcode
                    )
                ]
                csv_data = filtered_rows
                print(f"[OK] Linked CSV: {csv_file} ({len(filtered_rows)} matching records)")
                if len(filtered_rows) == 0:
                    zero_record_files.append({
                        'file': csv_file,
                        'vessel': vessel,
                        'batchcode': batchcode,
                        'reason': 'No matching rows for Vessel and Batch Code'
                    })
            except Exception as e:
                print(f"[ERROR] Failed to read {csv_file}: {e}")
        else:
            print(f"[WARN] CSV file not found: {csv_file}")
        merged.append({
            'file': csv_file,
            'csv_data': csv_data,
            'json_meta': entry
        })
    if not vessel_contents_all_in_index:
        vessel_contents_path = os.path.join(csv_dir, "vessel_contents_all.csv")
        if os.path.exists(vessel_contents_path):
            processed_groups = process_vessel_contents_all(vessel_contents_path, work_detailz_dict, fruit_intakes_dict)
            merged.extend(processed_groups)
            print(f"[OK] Added vessel_contents_all.csv (not in index) with {len(processed_groups)} groups")
        else:
            print("[WARN] vessel_contents_all.csv not found in directory")
    return merged, zero_record_files

def main():
    csv_reports_dir = r"Main/data/vintrace_reports/disp_reports"
    json_index_path = os.path.join(csv_reports_dir, "report_index.json")
    output_compact_json_path = os.path.join(csv_reports_dir, "linked_reports_compact.json")
    zero_records_json_path = os.path.join(csv_reports_dir, "zero_records_info.json")
    work_detailz_path = r"Main/data/vintrace_reports/work_detailz.json"
    fruit_intakes_extracted_path = r"Main/data/GET--fruit_intakes/tables/fr_fruit_intakes_extracted.json"

    sample_index_path = os.path.join(csv_reports_dir, "report_index_sample.json")
    sample_compact_linked_path = os.path.join(csv_reports_dir, "linked_reports_compact_sample.json")

    json_index = read_json_index(json_index_path, csv_reports_dir)
    work_detailz = load_work_detailz(work_detailz_path)
    fruit_intakes_extracted = load_fruit_intakes_extracted(fruit_intakes_extracted_path)
    work_detailz_dict, fruit_intakes_dict = build_lookup_dicts(work_detailz, fruit_intakes_extracted)

    merged_data, zero_record_files = merge_json_with_csv(json_index, csv_reports_dir, work_detailz_dict, fruit_intakes_dict)

    compact_data = []
    for e in merged_data:
        if e.get("file") == "vessel_contents_all.csv":
            compact_data.append(e)
        else:
            compact_data.append(compact_json_entry(e, work_detailz_dict, fruit_intakes_dict))

    build_weigh_tag_totals(compact_data)
    assign_relative_disp_gallons_frac(compact_data)

    with open(output_compact_json_path, 'w', encoding='utf-8') as outf2:
        json.dump(compact_data, outf2, indent=2)
    print(f"Compact linked report JSON written to: {output_compact_json_path}")

    if zero_record_files:
        with open(zero_records_json_path, 'w', encoding='utf-8') as zrf:
            json.dump(zero_record_files, zrf, indent=2)
        print(f"Zero-record info written to: {zero_records_json_path}")
    else:
        print("No zero-record CSVs detected.")

    with open(sample_index_path, 'w', encoding='utf-8') as sf1:
        json.dump(json_index[:10], sf1, indent=2)
    print(f"Sample report index written to: {sample_index_path}")

    with open(sample_compact_linked_path, 'w', encoding='utf-8') as sf3:
        json.dump(compact_data[:10], sf3, indent=2)
    print(f"Sample compact linked reports written to: {sample_compact_linked_path}")

if __name__ == "__main__":
    main()