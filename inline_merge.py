#!/usr/bin/env python3
"""
Inline merge execution
"""
import json
import os
from datetime import datetime

# Set the working directory
os.chdir('/Users/aliarsan/edliocustomermap')

# Load and analyze files
print("=== MERGE SCRIPT EXECUTION ===")

# Load current data
print("Loading current geocoded data...")
try:
    with open('apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    print(f"✓ Current data loaded: {len(current_data)} records")
except Exception as e:
    print(f"✗ Error loading current data: {e}")
    exit(1)

# Load batch data
print("Loading batch geocoded data...")
try:
    with open('apptegy-geocoded-batch.json', 'r') as f:
        batch_json = json.load(f)
        batch_data = batch_json.get('successful_geocodes', [])
    print(f"✓ Batch data loaded: {len(batch_data)} records")
    print(f"✓ Batch metadata: {batch_json.get('metadata', {})}")
except Exception as e:
    print(f"✗ Error loading batch data: {e}")
    exit(1)

# Show file stats
print(f"\nFile Statistics:")
print(f"Current dataset: {len(current_data)} records")
print(f"Batch dataset: {len(batch_data)} records")

# Execute the merge
print("\n=== EXECUTING MERGE ===")

# Copy code from merge_geocoded_data_v2.py
exec(open('merge_geocoded_data_v2.py').read())