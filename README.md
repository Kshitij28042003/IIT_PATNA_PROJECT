================================================================================
AUDIO INGESTION & MULTI-SLICE COLLECTION PIPELINE: RUN SEQUENCE GUIDE
================================================================================

This document defines the strict sequential workflow required to initialize,
populate, download, stitch, and audit audio assets for the multi-slice data
ingestion pipeline. Following this exact sequence prevents workspace 
corruption, preserves metadata validation, and maintains absolute data integrity.

--------------------------------------------------------------------------------
1. COMPLETE OPERATIONAL WORKFLOW SEQUENCE
--------------------------------------------------------------------------------

To ensure proper data tracking and prevent errors like overwriting curated 
parameters or crashing due to open files, you must execute the pipeline steps 
in the following chronological sequence:

   [ STEP 1 ] Manual Directory Creation
              |
              +---> Human setup establishing the taxonomy root ('dataset/')
              v
   [ STEP 2 ] init_multi_range_pipeline.py
              |
              +---> Establishes pipeline layout & quotas (Outputs batch_collect.csv)
              v
   [ STEP 3 ] Manual URL Curation Phase
              |
              +---> Human-in-the-loop links YouTube URLs & trims target seconds
              v
   [ STEP 4 ] count_urls.py
              |
              +---> Pre-flight sanity check mapping queued URLs
              v
   [ STEP 5 ] batch_collect.py
              |
              +---> Core Ingestion Engine (Downloads, Slices, Stitches, Logs)
              v
   [ STEP 6 ] verify_metadata.py
              |
              +---> Quality Assurance (Purges transients, computes metrics)

--------------------------------------------------------------------------------
2. DETAILED STEP-BY-STEP EXECUTION SPECIFICATIONS
--------------------------------------------------------------------------------

STEP 1: Manual Folder Structure & Taxonomy Creation
---------------------------------------------------
* Action: Before running any automation, you must manually construct your target
  data taxonomy folders inside your workspace root.
* Purpose: The initialization scripts scan the folder tree to determine your 
  "leaf nodes" (the deepest subfolders). Creating these directories ahead of 
  time dictates where data will be stored and how targets are split.
* Task: Create a base directory named 'dataset/'. Inside it, build your nesting 
  layers representing states, categories, and categories attributes.
  Example Schema:
    dataset/
    └── StateName/
        ├── AGE_GROUP/
        │   ├── Adolescent(13-19)/
        │   └── Adult(20-50)/
        └── EMOTION/
            ├── Surprised/
            └── Angry/

STEP 2: Pipeline Initialization & Layout Target Allocation
----------------------------------------------------------
* Script: init_multi_range_pipeline.py
* Purpose: Analyzes the local filesystem nested within the 'dataset/' root 
  folder you built in Step 1 to pinpoint "true leaf subdirectories". It 
  automatically distributes your global boundary target of 800 samples equally 
  among the discovered nodes.
* Mechanism: Outputs a fresh 'batch_collect.csv' work queue filled with rows 
  mapped to each target location, containing a default format mock time-range 
  value ('1-5, 9-10') to guide user entry.
* Command:
  python init_multi_range_pipeline.py
* Safeguard: If an active 'batch_collect.csv' already exists and contains 
  content, the script intercepts execution and forces a command-line 
  validation prompt ("Overwrite layout? (y/N)") to ensure you do not 
  accidentally destroy existing data.

STEP 3: Human-In-The-Loop URL Provisioning & Target Adjustments
---------------------------------------------------------------
* Action: Convert or open your workspace tracking sheet ('batch_collect.xlsx') 
  in an editor.
* Task: Manually replace the empty placeholder slots under the 'youtube_url' 
  column with valid links matching the assigned subcategory category row. 
* Customization: Modify the values under 'time_ranges_seconds' to reflect 
  precise content highlights. You can input singular ranges like '15-45' or 
  comma-separated compound segments like '10-20, 45-60, 90-115'. The 
  downstream engine slices and strings these matching segments into a singular 
  unified clip.

STEP 4: Queue Pre-Flight Auditing & Link Validation
---------------------------------------------------
* Script: count_urls.py
* Purpose: Reads the active tracking queue spreadsheet to extract metrics prior 
  to spinning up network resources.
* Mechanism: Automatically drops empty fields, cleans trailing whitespace gaps, 
  and filters rows containing pre-existing systemic error markers ('[ERROR]'). 
  It echoes a clear validation summary to the terminal.
* Command:
  python count_urls.py

STEP 5: Core Ingestion Engine & Multi-Slice Processing Loop
-----------------------------------------------------------
* Script: batch_collect.py
* Purpose: The workhorse execution script that connects to the network, 
  extracts assets, slices timeline arrays, and updates core metadata records.
* Mechanism: 
  1. Spawns 'yt_dlp' to pull targeted raw audio chunks down locally.
  2. Leverages 'pydub' to slice time fragments precisely according to 
     instructions provided in 'time_ranges_seconds', seamlessly stitching them 
     together.
  3. Appends a standardized row structural manifest entry containing generated 
     UUID keys ('clip_id'), localized source tracking paths, and segment 
     dimensions straight to 'parameta.xlsx'.
  4. Flushes success flags ('yes') or sanitizes and records exceptions 
     directly into the queue tracking columns ('success' and 
     'reasoning_layer') inside 'batch_collect.xlsx'.
* Command:
  python batch_collect.py
* Crash Recovery & Progress Checking: Includes an automated resume verification 
  feature. On launch, it indexes existing records in 'parameta.xlsx' to 
  identify already processed signatures ('folder_path' + 'source_url' + 
  'start_time'). If the script terminates unexpectedly, re-running it skips 
  completed tasks and resumes processing where it left off without duplicating 
  network workloads.

STEP 6: Post-Ingestion Workspace Integrity Audit & Status Check
---------------------------------------------------------------
* Script: verify_metadata.py
* Purpose: Runs a final evaluation across files on disk to clean up temporary 
  assets and calculate overall completion metrics.
* Mechanism:
  - Phase 1 (Staging Purge): Iterates through your 'dataset/' directories to 
    find and delete residual master clips ('raw_audio*', 'converted_audio.wav') 
    left behind by unexpected crashes or hard cancellations.
  - Phase 2 (Audit Log): Performs a physical walk across leaf folders, 
    counting verified '.wav' and '.mp3' outputs. It displays a dynamic 
    breakdown of collection densities per category node along with a project 
    milestone percentage.
* Command:
  python verify_metadata.py

--------------------------------------------------------------------------------
3. MISSION-CRITICAL RULES FOR PIPELINE OPERATION
--------------------------------------------------------------------------------

1. AVOID FILE LOCK ERRORS (PermissionError): 
   Always close 'batch_collect.xlsx' and 'parameta.xlsx' in Excel, LibreOffice, 
   or other spreadsheet viewers before running 'batch_collect.py'. The engine 
   requires direct read/write access to flush live tracking statuses and error 
   flags to disk. If a file is open in another program, the script will throw 
   a PermissionError and fail to update your progress logs.

2. SYSTEM DEPENDENCIES: 
   The execution utilities 'yt_dlp' and 'pydub' require system-level access to 
   binaries for media manipulation. Ensure 'ffmpeg' and 'ffprobe' are installed 
   on your operating system and fully declared in your system's global 
   environment PATH variables.

3. ERROR REMEDIATION: 
   If a row flags a 'no' state inside 'batch_collect.xlsx', review the companion 
   'reasoning_layer' cell to inspect the sanitized error trace (e.g., private 
   video, dead URL, or invalid timestamp ranges). Correct the error or update 
   the link, then clear the error flag to allow the ingestion loop to 
   re-evaluate the row.

================================================================================
