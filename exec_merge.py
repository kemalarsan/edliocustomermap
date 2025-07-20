#!/usr/bin/env python3
"""Execute merge directly"""
import json
import os
from datetime import datetime

# Change to the correct directory
os.chdir('/Users/aliarsan/edliocustomermap/')

# Execute the merge script content directly
exec("""
def convert_batch_record(batch_record):
    location = batch_record.get('location', {})
    address = location.get('address', {})
    state = address.get('state', '')
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

# Load current data
print("Loading current geocoded data...")
with open('apptegy-geocoded-current.json', 'r') as f:
    current_data = json.load(f)

# Load batch geocoded data
print("Loading batch geocoded data...")
with open('apptegy-geocoded-batch.json', 'r') as f:
    batch_json = json.load(f)
    batch_data = batch_json.get('successful_geocodes', [])

print(f"Current data: {len(current_data)} records")
print(f"Batch data: {len(batch_data)} records")

# Create a set of existing record IDs to avoid duplicates
existing_ids = {record['recordId'] for record in current_data}

# Merge new records
new_records = 0
for batch_record in batch_data:
    record_id = batch_record['record_id']
    if record_id not in existing_ids:
        converted_record = convert_batch_record(batch_record)
        current_data.append(converted_record)
        new_records += 1

print(f"Added {new_records} new records")
print(f"Total records after merge: {len(current_data)}")

# Backup current file
backup_name = f'apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
print(f"Creating backup: {backup_name}")
os.rename('apptegy-geocoded-current.json', backup_name)

# Save merged data
print("Saving merged data to apptegy-geocoded-current.json...")
with open('apptegy-geocoded-current.json', 'w') as f:
    json.dump(current_data, f, indent=2)

# Show statistics
print("\\nMerge Statistics:")
print(f"Previous dataset: {len(current_data) - new_records} records")
print(f"New records added: {new_records}")
print(f"Final dataset: {len(current_data)} records")

# Count by state
state_counts = {}
for record in current_data:
    state = record.get('state', 'Unknown')
    if state:
        state_counts[state] = state_counts.get(state, 0) + 1

print("\\nTop 10 states by competitor count:")
sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
for state, count in sorted_states:
    print(f"  {state}: {count} schools")

print(f"\\n✅ Merge complete! Total Apptegy competitors geocoded: {len(current_data)}")
""")