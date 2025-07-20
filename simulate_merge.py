#!/usr/bin/env python3
"""
Simulate what the merge script would do without actually executing it
"""
import json
import os
from datetime import datetime

print("=== MERGE SIMULATION ===")

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
for batch_record in batch_data:
    record_id = batch_record['record_id']
    if record_id not in existing_ids:
        new_records += 1

print(f"Would add {new_records} new records")
print(f"Total records after merge would be: {len(current_data) + new_records}")

# Analyze batch metadata
metadata = batch_json.get('metadata', {})
print(f"\nBatch Metadata:")
print(f"  Processed at: {metadata.get('processed_at', 'N/A')}")
print(f"  Total results: {metadata.get('total_results', 'N/A')}")
print(f"  Total errors: {metadata.get('total_errors', 'N/A')}")
print(f"  Success rate: {metadata.get('success_rate', 'N/A'):.2f}%")

# Show sample of states that would be added
states_to_add = {}
for batch_record in batch_data:
    record_id = batch_record['record_id']
    if record_id not in existing_ids:
        location = batch_record.get('location', {})
        address = location.get('address', {})
        state = address.get('state', 'Unknown')
        if state:
            states_to_add[state] = states_to_add.get(state, 0) + 1

print(f"\nStates that would be added (top 10):")
sorted_states = sorted(states_to_add.items(), key=lambda x: x[1], reverse=True)[:10]
for state, count in sorted_states:
    print(f"  {state}: {count} schools")

print(f"\n✅ Simulation complete! Would merge {new_records} new records from batch data.")