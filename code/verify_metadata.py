#verifies the number of downloaded samples per subfolder and it's metadata

import os

DATASET_ROOT = "dataset"
TARGET_SAMPLES = 800  # Total target boundary across your evenly distributed tree structure

if not os.path.exists(DATASET_ROOT):
    print(f"Error: Target path '{DATASET_ROOT}' does not exist on disk. Run your initialization loop first.")
    exit()

print("=====================================================================")
print("   PHASE 1: SCANNING WORKSPACE AND PURGING UNEDITED LEFTOVERS        ")
print("=====================================================================\n")

total_deleted_temp_files = 0

# Programmatically walk the target workspace tree to keep staging environments clean
for root, dirs, files in os.walk(DATASET_ROOT):
    for filename in files:
        file_path = os.path.join(root, filename)
        
        # Target intermediate unedited whole master clips left behind from crash loops or cancellations
        if filename.startswith("raw_audio") or filename == "converted_audio.wav":
            try:
                os.remove(file_path)
                print(f"-> Purged unedited master component: {file_path}")
                total_deleted_temp_files += 1
            except Exception as e:
                print(f"Could not remove transient asset {file_path}: {e}")

print(f"\nCleanup pass fully complete. Removed {total_deleted_temp_files} unedited master file fragments.\n")

print("=====================================================================")
print("   PHASE 2: VERIFIED BENCHMARK MULTI-SLICE SAMPLE COUNTS PER NODE    ")
print("=====================================================================\n")

# Flexible layout formatting adjusting cleanly to your dynamic leaf folder paths
print(f"{'DYNAMIC SUBCATEGORY PATH NODE':<65} | {'STITCHED SAMPLES'}")
print("-" * 85)

global_grand_total = 0

# Walk structurally to evaluate completed files across your custom tree nodes
for root, dirs, files in os.walk(DATASET_ROOT):
    # Only evaluate true leaf subdirectories containing final media payloads
    if not dirs:
        sample_files = [
            f for f in files 
            if os.path.isfile(os.path.join(root, f)) and f.lower().endswith(('.wav', '.mp3'))
        ]
        sample_count = len(sample_files)
        global_grand_total += sample_count
        
        normalized_display_path = root.replace(os.sep, "/")
        print(f"{normalized_display_path:<65} | {sample_count:<5}")

print("-" * 85)
print(f"TOTAL VALID COMBINED SAMPLES ACCUMULATED: {global_grand_total} / {TARGET_SAMPLES}")

# Progress metric tracking dashboard
completion_percentage = (global_grand_total / TARGET_SAMPLES) * 100
print(f"CURRENT DATASET COMPLETION: {completion_percentage:.2f}%")
print("=====================================================================\n")