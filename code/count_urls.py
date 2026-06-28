#counts given URLS in batch_collect.py

import os
import pandas as pd

QUEUE_FILE = "batch_collect.xlsx"

if not os.path.exists(QUEUE_FILE):
    print(f"Error: '{QUEUE_FILE}' not found in the current directory.")
    exit()

try:
    # Read the excel file
    df = pd.read_excel(QUEUE_FILE)
    
    if 'youtube_url' not in df.columns:
        print("Error: Could not find a 'youtube_url' column in the Excel sheet.")
        exit()
        
    # Extract the column, clean string gaps, and remove empty/NaN values
    urls = df['youtube_url'].dropna().astype(str).str.strip()
    
    # Filter out empty strings or rows that start with standard script errors
    valid_urls = urls[(urls != "") & (~urls.str.startswith("[ERROR]"))]
    
    total_rows = len(df)
    valid_count = len(valid_urls)
    unique_count = valid_urls.nunique()

    # Display findings
    print("=" * 45)
    print(f"📊 BATCH COLLECT EXCEL SUMMARY")
    print("=" * 45)
    print(f"Total rows in Excel sheet : {total_rows}")
    print(f"Total valid URLs found    : {valid_count}")
    print(f"Unique URLs inside queue  : {unique_count}")
    print("=" * 45)

except Exception as e:
    print(f"An error occurred while reading the file: {e}")