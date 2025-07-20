#!/usr/bin/env python3
import subprocess
import sys
import os

# Change to the correct directory
os.chdir('/Users/aliarsan/edliocustomermap/')

# Execute the merge script
print("Executing merge_geocoded_data_v2.py...")
print(f"Working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")

try:
    # Run the script and capture output
    process = subprocess.Popen(
        [sys.executable, 'merge_geocoded_data_v2.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/Users/aliarsan/edliocustomermap/'
    )
    
    # Read output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    # Get any remaining output
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout)
    if stderr:
        print("STDERR:", stderr)
    
    print(f"\nProcess completed with return code: {process.returncode}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()