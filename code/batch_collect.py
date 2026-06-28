import os
import csv
import re
import subprocess
from datetime import datetime
import pandas as pd
from pydub import AudioSegment
from yt_dlp import YoutubeDL

# --- WORKSPACE PATHS CONFIGURATION ---
QUEUE_FILE = "batch_collect.xlsx"
MAIN_METADATA_FILE = "parameta.xlsx"
TARGET_SAMPLES = 800

if not os.path.exists(QUEUE_FILE):
    print(f"Queue file '{QUEUE_FILE}' missing! Run your layout generator script first.")
    exit()

# --- RESUME & PROGRESS IDENTIFICATION LOGIC ---
processed_signatures = set()
current_sample_count = 0

if os.path.exists(MAIN_METADATA_FILE) and os.path.getsize(MAIN_METADATA_FILE) > 0:
    try:
        df_meta = pd.read_excel(MAIN_METADATA_FILE)
        current_sample_count = len(df_meta)
        
        if all(col in df_meta.columns for col in ['folder_path', 'source_url', 'start_time_seconds']):
            for _, r_meta in df_meta.iterrows():
                f_path = str(r_meta['folder_path']).strip()
                s_url = str(r_meta['source_url']).strip()
                
                t_sec = str(r_meta['start_time_seconds']).strip()
                if t_sec.endswith('.0'):
                    t_sec = t_sec[:-2]
                
                sig = f"{f_path}_{s_url}_{t_sec}"
                processed_signatures.add(sig)
                
        print(f"Loaded ledger. Found {current_sample_count} existing entries. Progress: {current_sample_count}/{TARGET_SAMPLES}")
    except Exception as e:
        print(f"Warning reading main metadata file ({e}). Starting fresh count.")

if current_sample_count >= TARGET_SAMPLES:
    print(f"Dataset already fully saturated! ({current_sample_count}/{TARGET_SAMPLES} samples accumulated).")
    exit()

# Read the execution queue configuration layout
# Force 'reasoning_layer' and 'success' columns as string type to accept text logs
queue_df = pd.read_excel(QUEUE_FILE)
if 'reasoning_layer' in queue_df.columns:
    queue_df['reasoning_layer'] = queue_df['reasoning_layer'].astype(object)
if 'success' in queue_df.columns:
    queue_df['success'] = queue_df['success'].astype(object)
else:
    queue_df['success'] = ""

print("Starting queue scanning loops...\n")


def save_queue_with_formatting(df, path):
    """Saves the DataFrame to Excel and forces generous, auto-fitted column widths."""
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='batch_collect')
        worksheet = writer.sheets['batch_collect']
        
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)


for index, row in queue_df.iterrows():
    if current_sample_count >= TARGET_SAMPLES:
        print(f"Target goal met! Exactly {current_sample_count} samples have been securely logged.")
        break

    url = str(row['youtube_url']).strip() if pd.notna(row['youtube_url']) else ""
    range_string = str(row['time_ranges_seconds']).strip() if pd.notna(row['time_ranges_seconds']) else ""
    folder_path = str(row['folder_path']).strip()
    layer = row['reasoning_layer'] if pd.notna(row['reasoning_layer']) else ""

    if not url or url == "" or url.startswith("[ERROR]"):
        continue

    current_signature = f"{folder_path}_{url}_{range_string}"

    if current_signature in processed_signatures:
        print(f"[SKIP] Row {index + 1}: Path-Segment matching signature already logged -> Skipping.")
        if queue_df.at[index, 'success'] != 'yes':
            queue_df.at[index, 'success'] = 'yes'
        continue

    audio_folder = folder_path.replace("/", os.sep)
    print(f"\n--- [START] Processing Row {index + 1}: Targeting Folder -> {audio_folder} ---")
    os.makedirs(audio_folder, exist_ok=True)
    
    # Clean workspace remnants
    for f in os.listdir(audio_folder):
        if f.startswith("raw_audio") or f == "converted_audio.wav":
            try: os.remove(os.path.join(audio_folder, f))
            except: pass

    try:
        # Download Master Stream Payload
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(audio_folder, "raw_audio.%(ext)s"),
            "noplaylist": True,
            "quiet": True
        }
        
        print(f"Downloading stream source payload for Row {index + 1}...")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown Title')
            
        downloaded_file = None
        for file in os.listdir(audio_folder):
            if file.startswith("raw_audio"):
                downloaded_file = os.path.join(audio_folder, file)
                break
                
        if downloaded_file is None:
            raise Exception("Stream payload download execution failed.")

        # Transcode via FFmpeg
        wav_path = os.path.join(audio_folder, "converted_audio.wav")
        subprocess.run(["ffmpeg", "-i", downloaded_file, wav_path, "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Audio slicing matrix processing
        full_audio = AudioSegment.from_wav(wav_path)
        combined_track = AudioSegment.empty()
        
        ranges = [r.strip() for r in range_string.split(",") if "-" in r]
        parsed_ranges_log = []
        
        for r in ranges:
            start_str, end_str = r.split("-")
            start_sec, end_sec = float(start_str), float(end_str)
            chunk = full_audio[int(start_sec * 1000) : int(end_sec * 1000)]
            combined_track += chunk
            parsed_ranges_log.append(f"{start_sec}s-{end_sec}s")
        
        if len(combined_track) == 0:
            raise ValueError("No valid timestamps found matching video length constraints.")

        # ID Generation Schema
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_tokens = [t.upper()[:4] for t in audio_folder.split(os.sep) if t and t != "dataset"]
        prefix = "_".join(folder_tokens)
        clip_id = f"MULTISLICE_{prefix}_{timestamp}"
        
        clip_path = os.path.join(audio_folder, f"{clip_id}.wav")
        combined_track.export(clip_path, format="wav")
        
        try:
            os.remove(downloaded_file)
            os.remove(wav_path)
        except:
            pass
        
        # CALCULATE DURATION FIRST BEFORE ASSEMBLING METADATA DICT (Fixes NameError)
        final_duration_seconds = len(combined_track) / 1000.0
        metadata_entry = {
            "clip_id": clip_id, "folder_path": folder_path, "source_url": url,
            "video_title": video_title, "start_time_seconds": range_string,
            "end_time_seconds": f"Stitched Total: {final_duration_seconds}s",
            "duration_seconds": int(final_duration_seconds),
            "file_path": clip_path.replace(os.sep, "/"),
            "reasoning_layer": f"Multi-Slice ({', '.join(parsed_ranges_log)})" if not layer or "[ERROR]" in str(layer) else layer
        }
        
        # Incremental spreadsheet logging for parameta.xlsx
        new_row_df = pd.DataFrame([metadata_entry])
        if os.path.exists(MAIN_METADATA_FILE) and os.path.getsize(MAIN_METADATA_FILE) > 0:
            try:
                existing_meta_df = pd.read_excel(MAIN_METADATA_FILE)
                updated_meta_df = pd.concat([existing_meta_df, new_row_df], ignore_index=True)
            except:
                updated_meta_df = new_row_df
        else:
            updated_meta_df = new_row_df
            
        with pd.ExcelWriter(MAIN_METADATA_FILE, engine='openpyxl') as writer:
            updated_meta_df.to_excel(writer, index=False, sheet_name='parameta')
            ws_meta = writer.sheets['parameta']
            for col in ws_meta.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws_meta.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
        current_sample_count += 1
        processed_signatures.add(current_signature)
        
        # --- SUCCESS UPDATE LOGIC ---
        queue_df.at[index, 'success'] = 'yes'
        if "[ERROR]" in str(layer):
            queue_df.at[index, 'reasoning_layer'] = f"Multi-Slice ({', '.join(parsed_ranges_log)})"
            
        try:
            save_queue_with_formatting(queue_df, QUEUE_FILE)
        except PermissionError:
            print(f"!!! [WARNING]: Could not flush success flags to '{QUEUE_FILE}' because Excel is open.")
            
        print(f"[SUCCESS] Row {index + 1}: Combined file stored at '{clip_path}'. Progress: {current_sample_count}/{TARGET_SAMPLES}")
        
    except Exception as e:
        error_msg = str(e).replace('\n', ' ')
        
        # Sanitize ANSI formatting codes
        error_msg = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', error_msg)
        error_msg = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', error_msg)
        
        print(f"[FAILURE] Row {index + 1} processing failed. Reason: {error_msg}")
        print(f"-> Injecting error markers into Row {index + 1}...")
        
        # --- FAILURE UPDATE LOGIC ---
        queue_df.at[index, 'reasoning_layer'] = f"[ERROR]: {error_msg}"
        queue_df.at[index, 'success'] = 'no'
        
        try:
            save_queue_with_formatting(queue_df, QUEUE_FILE)
            print(f"-> Successfully updated '{QUEUE_FILE}' with error diagnostics.")
        except PermissionError:
            print(f"!!! [WARNING]: Could not save error logs to '{QUEUE_FILE}' because the file is open in Excel.")
            print("Please close Excel to allow file-writes, but the collection process will continue running!")
        continue

print(f"\nProcessing pass fully completed. Dataset status: {current_sample_count}/{TARGET_SAMPLES} clips.")