import pandas as pd
import json
import time
import os
from urllib.parse import quote
import urllib.request
from datetime import datetime

def geocode_address(address, retry_count=3):
    """Use Nominatim (OpenStreetMap) to geocode addresses with retry logic"""
    for attempt in range(retry_count):
        try:
            # Clean and format address
            encoded_address = quote(address)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1&countrycodes=us"
            
            # Add headers to avoid being blocked
            headers = {
                'User-Agent': 'Edlio Customer Map Geocoder/1.0'
            }
            
            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode())
            
            if data and len(data) > 0:
                return float(data[0]['lat']), float(data[0]['lon'])
            return None, None
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"  Retry {attempt + 1} for {address}")
                time.sleep(2)
            else:
                print(f"  Error geocoding {address}: {e}")
                return None, None

def format_url(url):
    """Clean and format URL"""
    if pd.isna(url) or url == '' or url == 'N/A':
        return None
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def load_existing_geocodes():
    """Load previously geocoded data if exists"""
    if os.path.exists('geocoded_data.json'):
        with open('geocoded_data.json', 'r') as f:
            return json.load(f)
    return {}

def save_geocodes(geocoded_data):
    """Save geocoded data to JSON file"""
    with open('geocoded_data.json', 'w') as f:
        json.dump(geocoded_data, f, indent=2)

# Load existing geocoded data
geocoded_cache = load_existing_geocodes()
print(f"Loaded {len(geocoded_cache)} existing geocoded addresses")

# Read Excel files
print("\nReading Excel files...")
charter_df = pd.read_excel('MAP - Charter & Private Clients Address-2025-07-03-08-26-15.xlsx')
district_df = pd.read_excel('MAP - District Client Address-2025-07-03-08-26-06.xlsx')

all_customers = []
total_processed = 0
total_geocoded = 0
total_failed = 0

# Process charter and private schools
print(f"\nProcessing {len(charter_df)} charter/private schools...")
start_time = datetime.now()

for idx, row in charter_df.iterrows():
    name = str(row.get('School Name', 'Unknown School')).strip()
    url = format_url(row.get('Website'))
    
    if url:  # Only process if URL exists
        # Create full address
        street = str(row.get('Street Address', '')).strip()
        city = str(row.get('City Address', '')).strip()
        state = str(row.get('STATE', '')).strip()
        zip_code = str(row.get('Zip Address', '')).strip()
        
        full_address = f"{street}, {city}, {state} {zip_code}, USA"
        
        # Check cache first
        if full_address in geocoded_cache:
            lat, lng = geocoded_cache[full_address]['lat'], geocoded_cache[full_address]['lng']
            print(f"[{idx+1}/{len(charter_df)}] {name} - Using cached location")
        else:
            # Geocode address
            print(f"[{idx+1}/{len(charter_df)}] {name} - Geocoding...")
            lat, lng = geocode_address(full_address)
            
            if lat and lng:
                # Save to cache
                geocoded_cache[full_address] = {'lat': lat, 'lng': lng}
                total_geocoded += 1
            else:
                total_failed += 1
            
            # Be nice to the geocoding service
            time.sleep(1.5)  # Increased delay for safety
        
        if lat and lng:
            all_customers.append({
                'name': name,
                'lat': lat,
                'lng': lng,
                'url': url,
                'type': 'charter',
                'state': state
            })
        
        total_processed += 1
        
        # Save progress every 50 addresses
        if total_processed % 50 == 0:
            save_geocodes(geocoded_cache)
            elapsed = (datetime.now() - start_time).seconds
            print(f"  Progress saved. Elapsed: {elapsed}s, Rate: {total_geocoded}/{elapsed}s")

# Process district schools
print(f"\nProcessing {len(district_df)} district schools...")

for idx, row in district_df.iterrows():
    name = str(row.get('School Name', 'Unknown District')).strip()
    url = format_url(row.get('Website'))
    
    if url:  # Only process if URL exists
        # Create full address
        street = str(row.get('Street Address', '')).strip()
        city = str(row.get('City Address', '')).strip()
        state = str(row.get('STATE', '')).strip()
        zip_code = str(row.get('Zip Address', '')).strip()
        
        full_address = f"{street}, {city}, {state} {zip_code}, USA"
        
        # Check cache first
        if full_address in geocoded_cache:
            lat, lng = geocoded_cache[full_address]['lat'], geocoded_cache[full_address]['lng']
            print(f"[{idx+1}/{len(district_df)}] {name} - Using cached location")
        else:
            # Geocode address
            print(f"[{idx+1}/{len(district_df)}] {name} - Geocoding...")
            lat, lng = geocode_address(full_address)
            
            if lat and lng:
                # Save to cache
                geocoded_cache[full_address] = {'lat': lat, 'lng': lng}
                total_geocoded += 1
            else:
                total_failed += 1
            
            # Be nice to the geocoding service
            time.sleep(1.5)  # Increased delay for safety
        
        if lat and lng:
            all_customers.append({
                'name': name,
                'lat': lat,
                'lng': lng,
                'url': url,
                'type': 'district',
                'state': state
            })
        
        total_processed += 1
        
        # Save progress every 50 addresses
        if total_processed % 50 == 0:
            save_geocodes(geocoded_cache)
            elapsed = (datetime.now() - start_time).seconds
            print(f"  Progress saved. Elapsed: {elapsed}s, Rate: {total_geocoded}/{elapsed}s")

# Final save
save_geocodes(geocoded_cache)

print(f"\n=== Geocoding Complete ===")
print(f"Total processed: {total_processed}")
print(f"Successfully geocoded: {len(all_customers)}")
print(f"Failed to geocode: {total_failed}")
print(f"Total time: {(datetime.now() - start_time).seconds}s")

# Generate JavaScript file content
js_content = "// Real Edlio customer data from Excel files (fully geocoded)\n"
js_content += f"// Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
js_content += f"// Total customers: {len(all_customers)}\n"
js_content += "const customers = [\n"

for i, customer in enumerate(all_customers):
    # Escape quotes in names
    safe_name = customer['name'].replace('"', '\\"')
    js_content += f'    {{ name: "{safe_name}", lat: {customer["lat"]}, lng: {customer["lng"]}, url: "{customer["url"]}", type: "{customer["type"]}", state: "{customer["state"]}" }}'
    if i < len(all_customers) - 1:
        js_content += ","
    js_content += "\n"

js_content += "];"

# Write to data.js
with open('data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"\ndata.js has been updated with {len(all_customers)} real customers!")

# Also save customer data as JSON for backup
with open('customers_backup.json', 'w', encoding='utf-8') as f:
    json.dump(all_customers, f, indent=2)
print("Backup saved to customers_backup.json")