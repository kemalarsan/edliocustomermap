import pandas as pd
import json

# Read both Excel files
charter_df = pd.read_excel('MAP - Charter & Private Clients Address-2025-07-03-08-26-15.xlsx')
district_df = pd.read_excel('MAP - District Client Address-2025-07-03-08-26-06.xlsx')

# Function to clean and format URL
def format_url(url):
    if pd.isna(url) or url == '' or url == 'N/A':
        return None
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

# Process charter and private schools
charter_data = []
for _, row in charter_df.iterrows():
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        name = str(row.get('Name', 'Unknown School')).strip()
        url = format_url(row.get('URL'))
        if url:  # Only add if URL exists
            charter_data.append({
                'name': name,
                'lat': float(row['Latitude']),
                'lng': float(row['Longitude']),
                'url': url,
                'type': 'charter'
            })

# Process district schools
district_data = []
for _, row in district_df.iterrows():
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        name = str(row.get('Name', 'Unknown District')).strip()
        url = format_url(row.get('URL'))
        if url:  # Only add if URL exists
            district_data.append({
                'name': name,
                'lat': float(row['Latitude']),
                'lng': float(row['Longitude']),
                'url': url,
                'type': 'district'
            })

# Combine all data
all_customers = charter_data + district_data

print(f"Total charter/private schools: {len(charter_data)}")
print(f"Total districts: {len(district_data)}")
print(f"Total customers: {len(all_customers)}")

# Generate JavaScript file content
js_content = "// Real Edlio customer data from Excel files\n"
js_content += "const customers = [\n"

for i, customer in enumerate(all_customers):
    js_content += f"    {{ name: \"{customer['name']}\", lat: {customer['lat']}, lng: {customer['lng']}, url: \"{customer['url']}\", type: \"{customer['type']}\" }}"
    if i < len(all_customers) - 1:
        js_content += ","
    js_content += "\n"

js_content += "];"

# Write to data.js
with open('data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("\ndata.js has been updated with real customer data!")