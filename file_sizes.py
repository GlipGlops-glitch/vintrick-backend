#python file_sizes.py

import os
import csv

# Set your project root directory here
project_dir = r"C:\Users\cah01\Code\Vintrick\vintrick-backend"

output_csv = "file_sizes.csv"

with open(output_csv, "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["File Path", "Size (bytes)", "Size (MB)"])
    for root, dirs, files in os.walk(project_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                size_bytes = os.path.getsize(filepath)
                size_mb = round(size_bytes / (1024 * 1024), 2)
                writer.writerow([filepath, size_bytes, size_mb])
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

print(f"File size data saved to {output_csv}")