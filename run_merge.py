#!/usr/bin/env python3
"""
Wrapper script to run the merge script and capture output
"""
import subprocess
import sys
import os

# Change to the correct directory
os.chdir('/Users/aliarsan/edliocustomermap')

# Run the merge script
try:
    result = subprocess.run([sys.executable, 'merge_geocoded_data_v2.py'], 
                          capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
except Exception as e:
    print(f"Error running script: {e}")