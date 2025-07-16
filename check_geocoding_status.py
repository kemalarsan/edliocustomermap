#!/usr/bin/env python3
"""
Check the status of the geocoding process
"""

import json
import os
from datetime import datetime

PROGRESS_FILE = "geocoding_progress.json"
OUTPUT_FILE = "apptegy-geocoded-batch.json"

def check_status():
    """Check and display the current status of geocoding"""
    
    print("=== Apptegy Schools Geocoding Status ===\n")
    
    # Check progress file
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            
            print(f"Last processed index: {progress.get('last_processed_index', 'N/A')}")
            print(f"Successful geocodes: {len(progress.get('results', []))}")
            print(f"Failed attempts: {len(progress.get('errors', []))}")
            
            total = len(progress.get('results', [])) + len(progress.get('errors', []))
            if total > 0:
                success_rate = len(progress.get('results', [])) / total * 100
                print(f"Success rate: {success_rate:.1f}%")
            
            timestamp = progress.get('timestamp')
            if timestamp:
                print(f"Last updated: {timestamp}")
            
        except Exception as e:
            print(f"Error reading progress file: {e}")
    else:
        print("No progress file found - process hasn't started yet")
    
    print()
    
    # Check output file
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                output = json.load(f)
            
            metadata = output.get('metadata', {})
            print("=== Final Results ===")
            print(f"Total successful: {metadata.get('total_results', 'N/A')}")
            print(f"Total failed: {metadata.get('total_errors', 'N/A')}")
            print(f"Success rate: {metadata.get('success_rate', 'N/A'):.1f}%")
            print(f"Completed at: {metadata.get('processed_at', 'N/A')}")
            
        except Exception as e:
            print(f"Error reading output file: {e}")
    else:
        print("No final output file found - process not completed yet")

if __name__ == "__main__":
    check_status()