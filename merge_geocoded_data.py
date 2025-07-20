#!/usr/bin/env python3
"""
Merge the batch geocoded Apptegy data with the current dataset
"""
import json
import os
from datetime import datetime

def merge_geocoded_data():
    # Load current data
    print("Loading current geocoded data...")
    with open('apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    
    # Load batch geocoded data
    print("Loading batch geocoded data...")
    with open('apptegy-geocoded-batch.json', 'r') as f:
        batch_json = json.load(f)
        # Extract the successful_geocodes array from the nested structure
        batch_data = batch_json.get('successful_geocodes', [])
    
    print(f"Current data: {len(current_data)} records")
    print(f"Batch data: {len(batch_data)} records")
    
    # Create a set of existing record IDs to avoid duplicates
    existing_ids = {record['recordId'] for record in current_data}
    
    # Merge new records
    new_records = 0
    for record in batch_data:
        if record['recordId'] not in existing_ids:
            current_data.append(record)
            new_records += 1
    
    print(f"Added {new_records} new records")
    print(f"Total records after merge: {len(current_data)}")
    
    # Backup current file
    backup_name = f'apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    print(f"Creating backup: {backup_name}")
    os.rename('apptegy-geocoded-current.json', backup_name)
    
    # Save merged data
    print("Saving merged data to apptegy-geocoded-current.json...")
    with open('apptegy-geocoded-current.json', 'w') as f:
        json.dump(current_data, f, indent=2)
    
    # Show statistics
    print("\nMerge Statistics:")
    print(f"Previous dataset: {len(current_data) - new_records} records")
    print(f"New records added: {new_records}")
    print(f"Final dataset: {len(current_data)} records")
    
    # Count by state
    state_counts = {}
    for record in current_data:
        state = record.get('state', 'Unknown')
        state_counts[state] = state_counts.get(state, 0) + 1
    
    print("\nTop 10 states by competitor count:")
    sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for state, count in sorted_states:
        print(f"  {state}: {count} schools")

if __name__ == "__main__":
    merge_geocoded_data()