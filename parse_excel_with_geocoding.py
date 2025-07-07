import pandas as pd
import json
import time
from urllib.parse import quote
import urllib.request

def geocode_address(address):
    """Use Nominatim (OpenStreetMap) to geocode addresses"""
    try:
        # Clean and format address
        encoded_address = quote(address)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1&countrycodes=us"
        
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Edlio Customer Map Geocoder'
        }
        
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode())
        
        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
        return None, None
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None, None

# Function to clean and format URL
def format_url(url):
    if pd.isna(url) or url == '' or url == 'N/A':
        return None
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

# Read both Excel files
charter_df = pd.read_excel('MAP - Charter & Private Clients Address-2025-07-03-08-26-15.xlsx')
district_df = pd.read_excel('MAP - District Client Address-2025-07-03-08-26-06.xlsx')

print("Processing customer data...")
all_customers = []

# Process charter and private schools
print("\nProcessing charter/private schools...")
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
        
        # Geocode address
        print(f"Geocoding {idx+1}/{len(charter_df)}: {name}")
        lat, lng = geocode_address(full_address)
        
        if lat and lng:
            all_customers.append({
                'name': name,
                'lat': lat,
                'lng': lng,
                'url': url,
                'type': 'charter',
                'state': state
            })
        
        # Be nice to the geocoding service
        time.sleep(1)
        
        # Limit for testing (remove this line to process all)
        if idx >= 19:  # Process first 20
            break

# Process district schools
print("\nProcessing district schools...")
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
        
        # Geocode address
        print(f"Geocoding {idx+1}/{len(district_df)}: {name}")
        lat, lng = geocode_address(full_address)
        
        if lat and lng:
            all_customers.append({
                'name': name,
                'lat': lat,
                'lng': lng,
                'url': url,
                'type': 'district',
                'state': state
            })
        
        # Be nice to the geocoding service
        time.sleep(1)
        
        # Limit for testing (remove this line to process all)
        if idx >= 19:  # Process first 20
            break

print(f"\nTotal customers geocoded: {len(all_customers)}")

# Generate JavaScript file content
js_content = "// Real Edlio customer data from Excel files (with geocoded locations)\n"
js_content += "// Note: This is a sample of the data. Full geocoding takes time.\n"
js_content += "const customers = [\n"

for i, customer in enumerate(all_customers):
    js_content += f"    {{ name: \"{customer['name']}\", lat: {customer['lat']}, lng: {customer['lng']}, url: \"{customer['url']}\", type: \"{customer['type']}\", state: \"{customer['state']}\" }}"
    if i < len(all_customers) - 1:
        js_content += ","
    js_content += "\n"

js_content += "];"

# Write to data.js
with open('data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("\ndata.js has been updated with real customer data!")