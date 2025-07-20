#!/usr/bin/env python3
"""Simple merge implementation"""
import json
import os
from datetime import datetime

def main():
    # Load current data
    print("Loading current geocoded data...")
    with open('/Users/aliarsan/edliocustomermap/apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    print(f"Loaded {len(current_data)} records from current file")
    
    # Load batch data
    print("Loading batch geocoded data...")
    with open('/Users/aliarsan/edliocustomermap/apptegy-geocoded-batch.json', 'r') as f:
        batch_json = json.load(f)
        batch_data = batch_json.get('successful_geocodes', [])
    print(f"Loaded {len(batch_data)} records from batch file")
    
    # Find existing IDs
    existing_ids = {record['recordId'] for record in current_data}
    
    # Convert and merge
    new_records = 0
    for batch_record in batch_data:
        record_id = batch_record['record_id']
        if record_id not in existing_ids:
            location = batch_record.get('location', {})
            address = location.get('address', {})
            state = address.get('state', '')
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
    
    print(f"Added {new_records} new records")
    
    # Create backup
    backup_name = f'/Users/aliarsan/edliocustomermap/apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    os.rename('/Users/aliarsan/edliocustomermap/apptegy-geocoded-current.json', backup_name)
    print(f"Created backup: {backup_name}")
    
    # Save merged data
    with open('/Users/aliarsan/edliocustomermap/apptegy-geocoded-current.json', 'w') as f:
        json.dump(current_data, f, indent=2)
    print(f"Saved merged data: {len(current_data)} records")
    
    # Statistics
    print("\n=== MERGE STATISTICS ===")
    print(f"Previous dataset: {len(current_data) - new_records} records")
    print(f"New records added: {new_records}")
    print(f"Final dataset: {len(current_data)} records")
    
    # Count by state
    state_counts = {}
    for record in current_data:
        state = record.get('state', '')
        if state:
            state_counts[state] = state_counts.get(state, 0) + 1
    
    print("\nTop 10 states by competitor count:")
    sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for state, count in sorted_states:
        print(f"  {state}: {count} schools")
    
    print(f"\n✅ MERGE COMPLETE! Total records: {len(current_data)}")

if __name__ == "__main__":
    main()