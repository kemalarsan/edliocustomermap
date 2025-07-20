#!/usr/bin/env python3
"""Direct merge script with full output"""
import json
import os
from datetime import datetime

# Change to the correct directory
os.chdir('/Users/aliarsan/edliocustomermap/')

print("=== Starting Apptegy Geocoded Data Merge ===")
print(f"Working directory: {os.getcwd()}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load current data
print("\n1. Loading current geocoded data...")
try:
    with open('apptegy-geocoded-current.json', 'r') as f:
        current_data = json.load(f)
    print(f"   ✓ Loaded {len(current_data)} records from apptegy-geocoded-current.json")
except Exception as e:
    print(f"   ✗ Error loading current data: {e}")
    exit(1)

# Load batch geocoded data
print("\n2. Loading batch geocoded data...")
try:
    with open('apptegy-geocoded-batch.json', 'r') as f:
        batch_json = json.load(f)
        batch_data = batch_json.get('successful_geocodes', [])
    print(f"   ✓ Loaded {len(batch_data)} records from apptegy-geocoded-batch.json")
    print(f"   - Total results in batch file: {batch_json['metadata']['total_results']}")
    print(f"   - Success rate: {batch_json['metadata']['success_rate']:.2f}%")
except Exception as e:
    print(f"   ✗ Error loading batch data: {e}")
    exit(1)

# Create a set of existing record IDs
print("\n3. Analyzing existing records...")
existing_ids = {record['recordId'] for record in current_data}
print(f"   - Found {len(existing_ids)} unique record IDs in current dataset")

# Convert and merge records
print("\n4. Merging new records...")
new_records = 0
skipped_duplicates = 0

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
        
        # Print progress every 500 records
        if new_records % 500 == 0:
            print(f"   - Processed {new_records} new records...")
    else:
        skipped_duplicates += 1

print(f"   ✓ Added {new_records} new records")
print(f"   - Skipped {skipped_duplicates} duplicate records")

# Create backup
print("\n5. Creating backup...")
backup_name = f'apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
try:
    os.rename('apptegy-geocoded-current.json', backup_name)
    print(f"   ✓ Created backup: {backup_name}")
except Exception as e:
    print(f"   ✗ Error creating backup: {e}")
    exit(1)

# Save merged data
print("\n6. Saving merged data...")
try:
    with open('apptegy-geocoded-current.json', 'w') as f:
        json.dump(current_data, f, indent=2)
    print(f"   ✓ Saved {len(current_data)} records to apptegy-geocoded-current.json")
except Exception as e:
    print(f"   ✗ Error saving merged data: {e}")
    # Try to restore backup
    try:
        os.rename(backup_name, 'apptegy-geocoded-current.json')
        print(f"   ✓ Restored backup due to save error")
    except:
        pass
    exit(1)

# Calculate and display statistics
print("\n=== MERGE STATISTICS ===")
print(f"Previous dataset: {len(current_data) - new_records} records")
print(f"New records added: {new_records}")
print(f"Final dataset: {len(current_data)} records")
print(f"Expected total: {2301 + 5696} (2,301 current + 5,696 batch)")
print(f"Actual total: {len(current_data)}")

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

print(f"\n✅ MERGE COMPLETE!")
print(f"Total Apptegy competitors geocoded: {len(current_data)}")

# Verify the file was saved correctly
try:
    with open('apptegy-geocoded-current.json', 'r') as f:
        verify_data = json.load(f)
    print(f"\n✓ Verification: File contains {len(verify_data)} records")
except Exception as e:
    print(f"\n✗ Verification failed: {e}")