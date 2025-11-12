#    python tools/bit/backtrader_ORB_passes.py

import pandas as pd
import numpy as np

CSV_PATH = r'C:\Users\cah01\Code\Vintrick\vintrick-backend\tools\bit\btcusd_1-min_data.csv'
START_DATE = "2024-01-01"
END_DATE = "2025-10-31"
RANGE_SIZE = 2000
OUTPUT_CSV = r'C:\Users\cah01\Code\Vintrick\vintrick-backend\tools\bit\annual_range_passage_counts_and_time.csv'


def load_data(csv_path, start_date, end_date):
    df = pd.read_csv(csv_path)
    df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
    df.set_index('datetime', inplace=True)
    df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))].copy()
    df['year'] = df.index.year
    return df

def build_ranges(min_price, max_price, step):
    ranges = []
    for start in range(int(min_price), int(max_price), step):
        end = start + step
        ranges.append((start, end))
    return ranges

def log_range_passages(df, range_size):
    min_price = int(df['Low'].min() // range_size * range_size)
    max_price = int(df['High'].max() // range_size * range_size + range_size)
    ranges = build_ranges(min_price, max_price, range_size)
    range_labels = [f"{low}-{high}" for (low, high) in ranges]

    logs = []
    last_range_idx = None
    last_entry_time = None
    last_exit_time = None
    last_label = None
    last_year = None

    for i, row in df.iterrows():
        price = row['Close']
        year = row['year']
        range_idx = None
        for idx, (low, high) in enumerate(ranges):
            if low <= price < high:
                range_idx = idx
                break
        label = range_labels[range_idx] if range_idx is not None else None

        # If newly entered a range (not the same as previous)
        if range_idx is not None and range_idx != last_range_idx:
            # If leaving previous range, record the visit
            if last_range_idx is not None and last_entry_time is not None:
                logs.append({
                    "Year": last_year,
                    "Range": last_label,
                    "Start": last_entry_time,
                    "End": i,
                    "Minutes": int((i - last_entry_time).total_seconds() / 60),
                    "Hours": round((i - last_entry_time).total_seconds() / 3600, 2),
                })
            # Now entering new range
            last_entry_time = i
            last_label = label
            last_year = year
        last_range_idx = range_idx

    # Handle final range exit at end of data
    if last_range_idx is not None and last_entry_time is not None:
        end_time = df.index[-1]
        logs.append({
            "Year": last_year,
            "Range": last_label,
            "Start": last_entry_time,
            "End": end_time,
            "Minutes": int((end_time - last_entry_time).total_seconds() / 60),
            "Hours": round((end_time - last_entry_time).total_seconds() / 3600, 2),
        })
    return logs

def save_detailed_log_csv(logs, output_csv):
    df_out = pd.DataFrame(logs)
    df_out.to_csv(output_csv, index=False)
    print(f"Saved detailed logs to {output_csv}")

def main():
    df = load_data(CSV_PATH, START_DATE, END_DATE)
    logs = log_range_passages(df, RANGE_SIZE)
    save_detailed_log_csv(logs, OUTPUT_CSV)

if __name__ == "__main__":
    main()