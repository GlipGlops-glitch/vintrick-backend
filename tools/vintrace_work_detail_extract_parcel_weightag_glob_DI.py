#   python tools/vintrace_work_detail_extract_parcel_weightag_glob_DI.py
import os

def print_file_head(filepath, n=128):
    with open(filepath, "rb") as f:
        raw = f.read(n)
    print(f"\n=== File: {filepath} ===")
    print(f"Raw bytes (hex): {raw[:64].hex(' ')} ...")  # print first 64 bytes as hex
    try:
        print("\nAs UTF-8:\n", raw.decode("utf-8"))
    except Exception as e:
        print("\nNot UTF-8.", e)
    try:
        print("\nAs UTF-16:\n", raw.decode("utf-16"))
    except Exception as e:
        print("\nNot UTF-16.", e)
    try:
        print("\nAs TIS-620:\n", raw.decode("tis-620"))
    except Exception as e:
        print("\nNot TIS-620.", e)
    print("="*40)

if __name__ == "__main__":
    # You can edit these paths to test any files you want
    folder = "Main/data/vintrace_reports/work_detailz"
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isfile(path):
            print_file_head(path, n=128)
            # Remove "break" below to check all files in the folder
            break