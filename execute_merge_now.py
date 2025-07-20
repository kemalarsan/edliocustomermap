#!/usr/bin/env python3
import json
import subprocess
import sys

# First, count current records
try:
    with open('apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    print(f"Current records before merge: {len(current_data)}")
except Exception as e:
    print(f"Error reading current data: {e}")

# Now execute the merge script
print("\nExecuting merge script...")
try:
    result = subprocess.run([sys.executable, 'merge_geocoded_data_v2.py'], 
                          capture_output=True, text=True, cwd='/Users/aliarsan/edliocustomermap/')
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"Error executing merge script: {e}")

# Count records after merge
try:
    with open('apptegy-geocoded-current.json', 'r') as f:
        merged_data = json.load(f)
    print(f"\nRecords after merge: {len(merged_data)}")
except Exception as e:
    print(f"Error reading merged data: {e}")