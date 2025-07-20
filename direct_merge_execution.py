#!/usr/bin/env python3
"""
Direct execution of merge logic from merge_geocoded_data_v2.py
This script performs the merge without using subprocess
"""
import json
import os
from datetime import datetime

def convert_batch_record(batch_record):
    """Convert batch record format to current format"""
    location = batch_record.get('location', {})
    address = location.get('address', {})
    
    # Extract state from address
    state = address.get('state', '')
    
    # Extract city - prefer neighbourhood, then town, then city from address
    city = (address.get('neighbourhood') or 
            address.get('town') or 
            address.get('city') or 
            batch_record.get('existing_city', ''))
    
    return {
        "recordId": batch_record['record_id'],
        "name": batch_record['company_name'],
        "competitor": "Apptegy",
        "domain": batch_record.get('domain', ''),
        "city": city,
        "state": state,
        "owner": "Unknown",  # Not in batch data
        "createDate": batch_record.get('processed_at', ''),
        "lat": location.get('latitude'),
        "lng": location.get('longitude'),
        "type": "competitor",
        "products": ["CMS"],  # Default for Apptegy
        "customerType": "District",  # Default
        "arr": 0,  # Not in batch data
        "employees": 0,  # Not in batch data
        "lastContact": batch_record.get('processed_at', ''),
        "salesStage": "Competitor",
        "priority": "Medium"
    }

def main():
    # Ensure we're in the correct directory
    os.chdir('/Users/aliarsan/edliocustomermap/')
    
    print("=== APPTEGY GEOCODED DATA MERGE ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {os.getcwd()}")
    
    # Load current data
    print("\nLoading current geocoded data...")
    try:
        with open('apptegy-geocoded-current.json', 'r') as f:
            current_data = json.load(f)
        print(f"✓ Loaded {len(current_data)} records from apptegy-geocoded-current.json")
    except Exception as e:
        print(f"✗ Error loading current data: {e}")
        return
    
    # Load batch geocoded data
    print("\nLoading batch geocoded data...")
    try:
        with open('apptegy-geocoded-batch.json', 'r') as f:
            batch_json = json.load(f)
            batch_data = batch_json.get('successful_geocodes', [])
        print(f"✓ Loaded {len(batch_data)} records from apptegy-geocoded-batch.json")
        print(f"  - Total results in batch: {batch_json['metadata']['total_results']}")
        print(f"  - Total errors in batch: {batch_json['metadata']['total_errors']}")
        print(f"  - Success rate: {batch_json['metadata']['success_rate']:.2f}%")
    except Exception as e:
        print(f"✗ Error loading batch data: {e}")
        return
    
    print(f"\nCurrent data: {len(current_data)} records")
    print(f"Batch data: {len(batch_data)} records")
    
    # Create a set of existing record IDs to avoid duplicates
    existing_ids = {record['recordId'] for record in current_data}
    
    # Merge new records
    print("\nMerging records...")
    new_records = 0
    duplicate_records = 0
    
    for i, batch_record in enumerate(batch_data):
        record_id = batch_record['record_id']
        if record_id not in existing_ids:
            converted_record = convert_batch_record(batch_record)
            current_data.append(converted_record)
            new_records += 1
            if new_records % 500 == 0:
                print(f"  Processed {new_records} new records...")
        else:
            duplicate_records += 1
    
    print(f"✓ Added {new_records} new records")
    print(f"  Skipped {duplicate_records} duplicate records")
    print(f"Total records after merge: {len(current_data)}")
    
    # Backup current file
    backup_name = f'apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    print(f"\nCreating backup: {backup_name}")
    try:
        os.rename('apptegy-geocoded-current.json', backup_name)
        print(f"✓ Backup created successfully")
    except Exception as e:
        print(f"✗ Error creating backup: {e}")
        return
    
    # Save merged data
    print("\nSaving merged data to apptegy-geocoded-current.json...")
    try:
        with open('apptegy-geocoded-current.json', 'w') as f:
            json.dump(current_data, f, indent=2)
        print(f"✓ Saved successfully")
    except Exception as e:
        print(f"✗ Error saving merged data: {e}")
        # Try to restore backup
        try:
            os.rename(backup_name, 'apptegy-geocoded-current.json')
            print(f"✓ Restored backup")
        except:
            print(f"✗ Could not restore backup")
        return
    
    # Show statistics
    print("\n=== MERGE STATISTICS ===")
    print(f"Previous dataset: {len(current_data) - new_records} records")
    print(f"New records added: {new_records}")
    print(f"Final dataset: {len(current_data)} records")
    print(f"Expected total: {2301 + 5696} = 7,997 records")
    print(f"Actual total: {len(current_data)} records")
    
    # Count by state
    state_counts = {}
    for record in current_data:
        state = record.get('state', 'Unknown')
        if state:  # Only count non-empty states
            state_counts[state] = state_counts.get(state, 0) + 1
    
    print("\nTop 10 states by competitor count:")
    sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for state, count in sorted_states:
        print(f"  {state}: {count} schools")
    
    # Final verification
    print("\nVerifying saved file...")
    try:
        with open('apptegy-geocoded-current.json', 'r') as f:
            verify_data = json.load(f)
        print(f"✓ Verification successful: {len(verify_data)} records in file")
    except Exception as e:
        print(f"✗ Verification failed: {e}")
    
    print(f"\n✅ MERGE COMPLETE! Total Apptegy competitors geocoded: {len(current_data)}")

if __name__ == "__main__":
    main()