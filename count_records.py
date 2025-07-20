#!/usr/bin/env python3
"""Count records in both files"""
import json

print("Counting records in both files...")

# Count current records
try:
    with open('apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    print(f"Current file: {len(current_data)} records")
except Exception as e:
    print(f"Error reading current file: {e}")

# Count batch records
try:
    with open('apptegy-geocoded-batch.json', 'r') as f:
        batch_json = json.load(f)
        batch_data = batch_json.get('successful_geocodes', [])
    print(f"Batch file: {len(batch_data)} records")
    print(f"Batch metadata: {batch_json.get('metadata', {})}")
except Exception as e:
    print(f"Error reading batch file: {e}")

# Check for duplicates
try:
    existing_ids = {record['recordId'] for record in current_data}
    batch_ids = {record['record_id'] for record in batch_data}
    
    duplicates = existing_ids.intersection(batch_ids)
    unique_batch = batch_ids - existing_ids
    
    print(f"Duplicate records: {len(duplicates)}")
    print(f"Unique batch records: {len(unique_batch)}")
    print(f"Expected total after merge: {len(current_data) + len(unique_batch)}")
    
except Exception as e:
    print(f"Error checking duplicates: {e}")

print("Done.")