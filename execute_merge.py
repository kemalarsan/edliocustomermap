#!/usr/bin/env python3
"""
Execute the merge and report results
"""
import json
import os
from datetime import datetime
import subprocess
import sys

def execute_merge():
    print("🔄 Starting Apptegy Dataset Merge Process...")
    print("=" * 60)
    
    try:
        # Import and run the merge function directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("merge_module", "merge_geocoded_data_v2.py")
        merge_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(merge_module)
        
        # Execute the merge
        total_records = merge_module.merge_geocoded_data()
        
        print("=" * 60)
        print(f"✅ MERGE SUCCESSFUL!")
        print(f"📊 Total Apptegy competitors now: {total_records}")
        print(f"🚀 Ready for production upload!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during merge: {e}")
        print("🔧 Attempting manual merge...")
        
        # Manual merge fallback
        try:
            # Load current data
            with open('apptegy-geocoded-current.json', 'r') as f:
                current_data = json.load(f)
            
            # Load batch data  
            with open('apptegy-geocoded-batch.json', 'r') as f:
                batch_json = json.load(f)
                batch_data = batch_json.get('successful_geocodes', [])
            
            print(f"📋 Current records: {len(current_data)}")
            print(f"📋 Batch records: {len(batch_data)}")
            
            # Get existing IDs
            existing_ids = {record['recordId'] for record in current_data}
            
            # Add new records
            new_count = 0
            for batch_record in batch_data:
                if batch_record['record_id'] not in existing_ids:
                    # Convert batch format to current format
                    location = batch_record.get('location', {})
                    address = location.get('address', {})
                    
                    new_record = {
                        "recordId": batch_record['record_id'],
                        "name": batch_record['company_name'],
                        "competitor": "Apptegy",
                        "domain": batch_record.get('domain', ''),
                        "city": address.get('town', address.get('city', '')),
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
            
            # Backup and save
            backup_name = f'apptegy-geocoded-current-backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
            os.rename('apptegy-geocoded-current.json', backup_name)
            
            with open('apptegy-geocoded-current.json', 'w') as f:
                json.dump(current_data, f, indent=2)
            
            print(f"✅ Manual merge completed!")
            print(f"📊 Added {new_count} new records")
            print(f"📊 Total records: {len(current_data)}")
            print(f"💾 Backup created: {backup_name}")
            
            return True
            
        except Exception as e2:
            print(f"❌ Manual merge also failed: {e2}")
            return False

if __name__ == "__main__":
    success = execute_merge()
    if success:
        print("\n🎉 Ready to upload to production!")
    else:
        print("\n❌ Merge failed - manual intervention required")