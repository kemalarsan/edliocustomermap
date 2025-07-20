#!/usr/bin/env python3
"""
Comprehensive analysis of the geocoded data files
"""
import json
import os
from datetime import datetime

print("COMPREHENSIVE GEOCODED DATA ANALYSIS")
print("=" * 60)

# Analyze current file
try:
    with open('apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    
    current_size = os.path.getsize('apptegy-geocoded-current.json')
    
    print("\n1. CURRENT GEOCODED DATA (apptegy-geocoded-current.json):")
    print(f"   - Total records: {len(current_data)}")
    print(f"   - File size: {current_size:,} bytes ({current_size/1024/1024:.2f} MB)")
    
    # Count by state
    state_counts = {}
    for record in current_data:
        state = record.get('state', 'Unknown')
        if state:
            state_counts[state] = state_counts.get(state, 0) + 1
    
    print(f"   - Number of states: {len(state_counts)}")
    print("\n   Top 5 states:")
    sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for state, count in sorted_states:
        print(f"     - {state}: {count} schools")
    
except Exception as e:
    print(f"\n   ERROR reading current file: {e}")

# Analyze batch file
try:
    with open('apptegy-geocoded-batch.json', 'r') as f:
        batch_json = json.load(f)
    
    batch_data = batch_json.get('successful_geocodes', [])
    metadata = batch_json.get('metadata', {})
    batch_size = os.path.getsize('apptegy-geocoded-batch.json')
    
    print("\n2. BATCH GEOCODED DATA (apptegy-geocoded-batch.json):")
    print(f"   - Successful geocodes: {len(batch_data)}")
    print(f"   - Total results: {metadata.get('total_results', 'N/A')}")
    print(f"   - Total errors: {metadata.get('total_errors', 'N/A')}")
    print(f"   - Success rate: {metadata.get('success_rate', 'N/A'):.2f}%")
    print(f"   - File size: {batch_size:,} bytes ({batch_size/1024/1024:.2f} MB)")
    print(f"   - Processed at: {metadata.get('processed_at', 'N/A')}")
    
except Exception as e:
    print(f"\n   ERROR reading batch file: {e}")

# Estimate merged size
try:
    existing_ids = {record['recordId'] for record in current_data}
    new_records = sum(1 for record in batch_data if record['record_id'] not in existing_ids)
    
    print("\n3. MERGE PREVIEW:")
    print(f"   - Current records: {len(current_data)}")
    print(f"   - New records to add: {new_records}")
    print(f"   - Expected total after merge: {len(current_data) + new_records}")
    
    # Estimate file size (rough approximation)
    avg_record_size = current_size / len(current_data) if len(current_data) > 0 else 0
    estimated_new_size = current_size + (new_records * avg_record_size)
    print(f"   - Estimated file size after merge: {estimated_new_size:,} bytes ({estimated_new_size/1024/1024:.2f} MB)")
    
except Exception as e:
    print(f"\n   ERROR in merge preview: {e}")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")

# Save analysis to file
with open('merge_analysis_report.txt', 'w') as f:
    f.write(f"Merge Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Current records: {len(current_data)}\n")
    f.write(f"New records to add: {new_records}\n")
    f.write(f"Expected total: {len(current_data) + new_records}\n")
    f.write(f"Current file size: {current_size/1024/1024:.2f} MB\n")
    f.write(f"Estimated new size: {estimated_new_size/1024/1024:.2f} MB\n")

print("\nAnalysis saved to merge_analysis_report.txt")