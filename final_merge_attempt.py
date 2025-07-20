#!/usr/bin/env python3
"""Final merge attempt - comprehensive execution"""
import json
import os
from datetime import datetime

def main():
    print("=== APPTEGY GEOCODED DATA MERGE - FINAL ATTEMPT ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Navigate to the correct directory
    base_dir = '/Users/aliarsan/edliocustomermap'
    os.chdir(base_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Files to work with
    current_file = 'apptegy-geocoded-current.json'
    batch_file = 'apptegy-geocoded-batch.json'
    
    try:
        # Load current data
        print(f"\\nLoading current data from {current_file}...")
        with open(current_file, 'r') as f:
            current_data = json.load(f)
        print(f"✓ Loaded {len(current_data)} records")
        
        # Load batch data
        print(f"\\nLoading batch data from {batch_file}...")
        with open(batch_file, 'r') as f:
            batch_json = json.load(f)
            batch_data = batch_json.get('successful_geocodes', [])
        print(f"✓ Loaded {len(batch_data)} records")
        print(f"  Batch metadata: {batch_json.get('metadata', {})}")
        
        # Analyze duplicates
        print(f"\\nAnalyzing for duplicates...")
        existing_ids = {record['recordId'] for record in current_data}
        batch_ids = {record['record_id'] for record in batch_data}
        duplicates = existing_ids.intersection(batch_ids)
        unique_batch = batch_ids - existing_ids
        
        print(f"  Current dataset IDs: {len(existing_ids)}")
        print(f"  Batch dataset IDs: {len(batch_ids)}")
        print(f"  Duplicate IDs: {len(duplicates)}")
        print(f"  Unique batch IDs: {len(unique_batch)}")
        
        # Convert and merge new records
        print(f"\\nMerging {len(unique_batch)} new records...")
        new_records = 0
        
        for batch_record in batch_data:
            record_id = batch_record['record_id']
            if record_id not in existing_ids:
                # Convert batch record to current format
                location = batch_record.get('location', {})
                address = location.get('address', {})
                
                # Extract state from address
                state = address.get('state', '')
                
                # Extract city - prefer neighbourhood, then town, then city from address
                city = (address.get('neighbourhood') or 
                        address.get('town') or 
                        address.get('city') or 
                        batch_record.get('existing_city', ''))
                
                converted_record = {
                    "recordId": batch_record['record_id'],
                    "name": batch_record['company_name'],
                    "competitor": "Apptegy",
                    "domain": batch_record.get('domain', ''),
                    "city": city,
                    "state": state,
                    "owner": "Unknown",
                    "createDate": batch_record.get('processed_at', ''),
                    "lat": location.get('latitude'),
                    "lng": location.get('longitude'),
                    "type": "competitor",
                    "products": ["CMS"],
                    "customerType": "District",
                    "arr": 0,
                    "employees": 0,
                    "lastContact": batch_record.get('processed_at', ''),
                    "salesStage": "Competitor",
                    "priority": "Medium"
                }
                
                current_data.append(converted_record)
                new_records += 1
                
                # Progress indicator
                if new_records % 1000 == 0:
                    print(f"  Processed {new_records} records...")
        
        print(f"✓ Added {new_records} new records")
        print(f"  Total records after merge: {len(current_data)}")
        
        # Create backup
        backup_name = f'apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        print(f"\\nCreating backup: {backup_name}")
        os.rename(current_file, backup_name)
        print(f"✓ Backup created")
        
        # Save merged data
        print(f"\\nSaving merged data to {current_file}...")
        with open(current_file, 'w') as f:
            json.dump(current_data, f, indent=2)
        print(f"✓ Saved {len(current_data)} records")
        
        # Generate statistics
        print(f"\\n=== MERGE STATISTICS ===")
        print(f"Original dataset: {len(current_data) - new_records} records")
        print(f"New records added: {new_records}")
        print(f"Final dataset: {len(current_data)} records")
        print(f"Expected total: {2301 + 5696} = 7,997 records")
        print(f"Actual total: {len(current_data)} records")
        
        # Count by state
        state_counts = {}
        for record in current_data:
            state = record.get('state', '')
            if state:
                state_counts[state] = state_counts.get(state, 0) + 1
        
        print(f"\\nTop 10 states by competitor count:")
        sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for state, count in sorted_states:
            print(f"  {state}: {count} schools")
        
        # Final verification
        print(f"\\nVerifying saved file...")
        with open(current_file, 'r') as f:
            verify_data = json.load(f)
        print(f"✓ Verification successful: {len(verify_data)} records in file")
        
        print(f"\\n✅ MERGE COMPLETE!")
        print(f"Total Apptegy competitors geocoded: {len(current_data)}")
        print(f"Backup created: {backup_name}")
        
    except Exception as e:
        print(f"\\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()