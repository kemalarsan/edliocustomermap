#!/usr/bin/env python3
import subprocess
import sys

# Run the merge script
result = subprocess.run([sys.executable, 'merge_geocoded_data_v2.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)