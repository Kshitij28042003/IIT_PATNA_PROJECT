#generates the batch_collect.csv file and puts in basic entries 

import os
import csv
import math

DATASET_ROOT = "dataset"
QUEUE_FILE = "batch_collect.csv"  # Updated to output straight to your main csv file
TOTAL_TARGET_SAMPLES = 800

if not os.path.exists(DATASET_ROOT):
    print(f"Error: '{DATASET_ROOT}' directory not found. Please set up your subfolder structure first!")
    exit()

# Scan recursively for true leaf folders (subcategories containing no deeper subfolders)
leaf_folders = []
for root, dirs, files in os.walk(DATASET_ROOT):
    if not dirs:  # Leaf node
        leaf_folders.append(root)

num_leaves = len(leaf_folders)
if num_leaves == 0:
    print("No subfolders detected inside the dataset root directory.")
    exit()

print(f"Detected {num_leaves} distinct subcategory leaf folders inside your structure.")

# Calculate even distribution parameters
base_allocation = TOTAL_TARGET_SAMPLES // num_leaves
remainder = TOTAL_TARGET_SAMPLES % num_leaves

# Columns matching the multi-slice ingestion engine format
headers = ["folder_path", "youtube_url", "time_ranges_seconds", "reasoning_layer"]

# Safeguard check to avoid accidentally blowing away a curated configuration spreadsheet
if os.path.exists(QUEUE_FILE) and os.path.getsize(QUEUE_FILE) > 0:
    choice = input(f"Warning: '{QUEUE_FILE}' already exists. Overwrite layout? (y/N): ").strip().lower()
    if choice != 'y':
        print("Aborting generation to save existing work.")
        exit()

print(f"Allocating rows to generate exactly {TOTAL_TARGET_SAMPLES} configuration slots...")
with open(QUEUE_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(headers)
    
    for idx, path in enumerate(sorted(leaf_folders)):
        # Calculate row counts cleanly per subcategory block
        allocated_rows = base_allocation + (1 if idx < remainder else 0)
        normalized_path = path.replace(os.sep, "/")
        
        # Write the allocated duplicate rows for this specific folder path
        for _ in range(allocated_rows):
            # Pre-populating an example format '1-5, 9-10' as requested
            writer.writerow([normalized_path, "", "1-5, 9-10", ""])

print(f"Successfully generated '{QUEUE_FILE}' with exactly {TOTAL_TARGET_SAMPLES} rows distributed across your subcategories.")
print("Format your entries like: 1-5, 9-10, 14-20 inside the 'time_ranges_seconds' column for each URL.")