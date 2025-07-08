import pandas as pd
import json
import os
from datetime import datetime

def format_url(url):
    """Clean and format URL"""
    if pd.isna(url) or url == '' or url == 'N/A':
        return None
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

# Load geocoded cache
with open('geocoded_data.json', 'r') as f:
    geocoded_cache = json.load(f)

print(f"Found {len(geocoded_cache)} geocoded addresses")

# Read Excel files
charter_df = pd.read_excel('MAP - Charter & Private Clients Address-2025-07-03-08-26-15.xlsx')
district_df = pd.read_excel('MAP - District Client Address-2025-07-03-08-26-06.xlsx')

all_customers = []

# Process charter and private schools
for idx, row in charter_df.iterrows():
    name = str(row.get('School Name', 'Unknown School')).strip()
    url = format_url(row.get('Website'))
    
    if url:
        street = str(row.get('Street Address', '')).strip()
        city = str(row.get('City Address', '')).strip()
        state = str(row.get('STATE', '')).strip()
        zip_code = str(row.get('Zip Address', '')).strip()
        
        full_address = f"{street}, {city}, {state} {zip_code}, USA"
        
        if full_address in geocoded_cache:
            lat = geocoded_cache[full_address]['lat']
            lng = geocoded_cache[full_address]['lng']
            
            all_customers.append({
                'name': name,
                'lat': lat,
                'lng': lng,
                'url': url,
                'type': 'charter',
                'state': state
            })

# Process district schools
for idx, row in district_df.iterrows():
    name = str(row.get('School Name', 'Unknown District')).strip()
    url = format_url(row.get('Website'))
    
    if url:
        street = str(row.get('Street Address', '')).strip()
        city = str(row.get('City Address', '')).strip()
        state = str(row.get('STATE', '')).strip()
        zip_code = str(row.get('Zip Address', '')).strip()
        
        full_address = f"{street}, {city}, {state} {zip_code}, USA"
        
        if full_address in geocoded_cache:
            lat = geocoded_cache[full_address]['lat']
            lng = geocoded_cache[full_address]['lng']
            
            all_customers.append({
                'name': name,
                'lat': lat,
                'lng': lng,
                'url': url,
                'type': 'district',
                'state': state
            })

print(f"Total customers with geocoded locations: {len(all_customers)}")

# Generate JavaScript file content
js_content = "// Real Edlio customer data from Excel files (partial geocoding)\n"
js_content += f"// Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
js_content += f"// Total customers: {len(all_customers)} (geocoding in progress...)\n"
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

print(f"data.js has been updated with {len(all_customers)} customers!")

# Save backup
with open('customers_backup.json', 'w', encoding='utf-8') as f:
    json.dump(all_customers, f, indent=2)