#!/usr/bin/env python3
"""
Check data status and perform merge
"""
import json
import os
from datetime import datetime

def check_data_status():
    print("=== Apptegy Geocoding Data Status ===\n")
    
    # Check current data
    try:
        with open('apptegy-geocoded-current.json', 'r') as f:
            current_data = json.load(f)
        print(f"✓ Current dataset: {len(current_data)} records")
    except Exception as e:
        print(f"✗ Error reading current data: {e}")
        return
    
    # Check batch data
    try:
        with open('apptegy-geocoded-batch.json', 'r') as f:
            batch_json = json.load(f)
        
        metadata = batch_json.get('metadata', {})
        batch_data = batch_json.get('successful_geocodes', [])
        
        print(f"✓ Batch dataset: {len(batch_data)} records")
        print(f"✓ Success rate: {metadata.get('success_rate', 0):.1f}%")
        print(f"✓ Total processed: {metadata.get('total_results', 0) + metadata.get('total_errors', 0)}")
        print(f"✓ Completion time: {metadata.get('processed_at', 'Unknown')}")
        
    except Exception as e:
        print(f"✗ Error reading batch data: {e}")
        return
    
    # Check for overlap
    current_ids = {record['recordId'] for record in current_data}
    batch_ids = {record['record_id'] for record in batch_data}
    
    overlap = len(current_ids.intersection(batch_ids))
    new_records = len(batch_ids - current_ids)
    
    print(f"\n=== Merge Preview ===")
    print(f"Current records: {len(current_data)}")
    print(f"Batch records: {len(batch_data)}")
    print(f"Overlapping IDs: {overlap}")
    print(f"New records to add: {new_records}")
    print(f"Total after merge: {len(current_data) + new_records}")
    
    return True

if __name__ == "__main__":
    check_data_status()