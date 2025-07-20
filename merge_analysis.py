#!/usr/bin/env python3
"""
Manual analysis of what the merge script would do
"""
import json
import os
from datetime import datetime

def analyze_merge():
    print("=== MERGE ANALYSIS REPORT ===")
    
    # Load current data
    print("Loading current geocoded data...")
    with open('/Users/aliarsan/edliocustomermap/apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    
    # Load batch geocoded data
    print("Loading batch geocoded data...")
    with open('/Users/aliarsan/edliocustomermap/apptegy-geocoded-batch.json', 'r') as f:
        batch_json = json.load(f)
        batch_data = batch_json.get('successful_geocodes', [])
    
    print(f"Current data: {len(current_data)} records")
    print(f"Batch data: {len(batch_data)} records")
    
    # Create a set of existing record IDs to avoid duplicates
    existing_ids = {record['recordId'] for record in current_data}
    
    # Count potential new records
    new_records = 0
    duplicate_records = 0
    
    for batch_record in batch_data:
        record_id = batch_record['record_id']
        if record_id not in existing_ids:
            new_records += 1
        else:
            duplicate_records += 1
    
    print(f"\nMerge Analysis:")
    print(f"Records that would be added: {new_records}")
    print(f"Duplicate records (skipped): {duplicate_records}")
    print(f"Total records after merge: {len(current_data) + new_records}")
    
    # Analyze batch metadata
    metadata = batch_json.get('metadata', {})
    print(f"\nBatch Processing Metadata:")
    print(f"  Processed at: {metadata.get('processed_at', 'N/A')}")
    print(f"  Total geocoding results: {metadata.get('total_results', 'N/A')}")
    print(f"  Total geocoding errors: {metadata.get('total_errors', 'N/A')}")
    print(f"  Success rate: {metadata.get('success_rate', 0):.2f}%")
    print(f"  Last processed index: {metadata.get('last_processed_index', 'N/A')}")
    
    # Analyze states that would be added
    states_to_add = {}
    for batch_record in batch_data:
        record_id = batch_record['record_id']
        if record_id not in existing_ids:
            location = batch_record.get('location', {})
            address = location.get('address', {})
            state = address.get('state', 'Unknown')
            if state:
                states_to_add[state] = states_to_add.get(state, 0) + 1
    
    print(f"\nStates distribution of new records (top 10):")
    sorted_states = sorted(states_to_add.items(), key=lambda x: x[1], reverse=True)[:10]
    for state, count in sorted_states:
        print(f"  {state}: {count} schools")
    
    # Show sample conversion
    if batch_data:
        print(f"\nSample record conversion:")
        sample_record = batch_data[0]
        print(f"Original batch record ID: {sample_record['record_id']}")
        print(f"Company name: {sample_record['company_name']}")
        location = sample_record.get('location', {})
        address = location.get('address', {})
        print(f"State: {address.get('state', 'N/A')}")
        print(f"City: {address.get('neighbourhood') or address.get('town') or address.get('city', 'N/A')}")
        print(f"Coordinates: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
    
    print(f"\n✅ Analysis complete! Ready to merge {new_records} new records.")
    
    return len(current_data), new_records, len(current_data) + new_records

if __name__ == "__main__":
    analyze_merge()