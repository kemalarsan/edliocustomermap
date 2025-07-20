#!/usr/bin/env python3
"""
Manually execute the merge and backup
"""
import json
import os
from datetime import datetime

# Read current data
with open('apptegy-geocoded-current.json', 'r') as f:
    current_data = json.load(f)

# Read batch data
with open('apptegy-geocoded-batch.json', 'r') as f:
    batch_json = json.load(f)
    batch_data = batch_json.get('successful_geocodes', [])

print(f"Current records: {len(current_data)}")
print(f"Batch records: {len(batch_data)}")

# Get existing IDs
existing_ids = {record['recordId'] for record in current_data}

# Add new records
new_count = 0
for batch_record in batch_data:
    if batch_record['record_id'] not in existing_ids:
        location = batch_record.get('location', {})
        address = location.get('address', {})
        
        new_record = {
            "recordId": batch_record['record_id'],
            "name": batch_record['company_name'],
            "competitor": "Apptegy",
            "domain": batch_record.get('domain', ''),
            "city": address.get('town', address.get('city', address.get('neighbourhood', ''))),
            "state": address.get('state', ''),
            "owner": "Geocoded",
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
        current_data.append(new_record)
        new_count += 1

# Create backup
backup_name = f'apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
os.rename('apptegy-geocoded-current.json', backup_name)

# Save merged data
with open('apptegy-geocoded-current.json', 'w') as f:
    json.dump(current_data, f, indent=2)

print(f"✅ Merge completed!")
print(f"📊 Added {new_count} new records")
print(f"📊 Total records: {len(current_data)}")
print(f"💾 Backup created: {backup_name}")

# State breakdown
state_counts = {}
for record in current_data:
    state = record.get('state', '')
    if state:
        state_counts[state] = state_counts.get(state, 0) + 1

print("\nTop 10 states by competitor count:")
sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
for state, count in sorted_states:
    print(f"  {state}: {count} schools")

print(f"\nReady to upload {len(current_data)} Apptegy competitors to production!")