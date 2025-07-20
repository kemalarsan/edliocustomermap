#!/usr/bin/env python3
"""
Analyze and merge geocoded data
"""
import json
import os
from datetime import datetime

# Load current data
print("Loading current geocoded data...")
with open('apptegy-geocoded-current.json', 'r') as f:
    current_data = json.load(f)

# Load batch geocoded data
print("Loading batch geocoded data...")
with open('apptegy-geocoded-batch.json', 'r') as f:
    batch_json = json.load(f)
    batch_data = batch_json.get('successful_geocodes', [])

print(f"\nCurrent data: {len(current_data)} records")
print(f"Batch data: {len(batch_data)} records")

# Get file sizes
current_size = os.path.getsize('apptegy-geocoded-current.json')
batch_size = os.path.getsize('apptegy-geocoded-batch.json')
print(f"\nCurrent file size: {current_size:,} bytes ({current_size/1024/1024:.2f} MB)")
print(f"Batch file size: {batch_size:,} bytes ({batch_size/1024/1024:.2f} MB)")

# Now run the actual merge
print("\n" + "="*50)
print("Running merge...")
print("="*50 + "\n")

# Import and run the merge function
import merge_geocoded_data_v2
total = merge_geocoded_data_v2.merge_geocoded_data()

# Get new file size
new_size = os.path.getsize('apptegy-geocoded-current.json')
print(f"\nNew file size after merge: {new_size:,} bytes ({new_size/1024/1024:.2f} MB)")
print(f"File size increase: {new_size - current_size:,} bytes ({(new_size - current_size)/1024/1024:.2f} MB)")