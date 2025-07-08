#!/usr/bin/env python3
"""
Smart geocoding script with deduplication.
Only geocodes addresses that aren't already in our cache.
"""

import pandas as pd
import json
import requests
import time
import re
from datetime import datetime

def clean_address(address_parts):
    """Clean and format address for geocoding"""
    # Remove NaN values and convert to strings
    clean_parts = []
    for part in address_parts:
        if pd.notna(part) and str(part).strip():
            clean_parts.append(str(part).strip())
    
    # Join with commas
    full_address = ', '.join(clean_parts)
    
    # Clean up common issues
    full_address = re.sub(r'\s+', ' ', full_address)  # Multiple spaces
    full_address = re.sub(r',\s*,', ',', full_address)  # Double commas
    full_address = full_address.strip(', ')
    
    return full_address

def load_existing_cache():
    """Load existing geocoded addresses"""
    try:
        with open('geocoded_data.json', 'r') as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} existing geocoded addresses from cache")
        return cache
    except FileNotFoundError:
        print("No existing cache found, starting fresh")
        return {}

def geocode_address(address, retry_count=3):
    """Geocode an address using Nominatim API with retry logic"""
    for attempt in range(retry_count):
        try:
            # Nominatim API (OpenStreetMap)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'EdlioCustomerMap/1.0 (educational-mapping)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                result = data[0]
                return {
                    'lat': float(result['lat']),
                    'lng': float(result['lon'])
                }
            else:
                return None
                
        except Exception as e:
            print(f"  Retry {attempt + 1} for {address[:50]}... Error: {e}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            
    return None

def save_progress(cache, customer_data):
    """Save current progress"""
    # Save geocoded cache
    with open('geocoded_data.json', 'w') as f:
        json.dump(cache, f, indent=2)
    
    # Save customer data
    with open('data.js', 'w') as f:
        f.write("// Real Edlio customer data from Excel files (with deduplication)\n")
        f.write(f"// Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"// Total customers: {len(customer_data)}\n")
        f.write("const customers = [\n")
        
        for customer in customer_data:
            f.write(f'    {{ name: "{customer["name"]}", lat: {customer["lat"]}, lng: {customer["lng"]}, url: "{customer["url"]}", type: "{customer["type"]}", state: "{customer["state"]}" }},\n')
        
        f.write("];\n")

def determine_school_type(name):
    """Determine school type based on name"""
    name_lower = name.lower()
    
    if any(word in name_lower for word in ['catholic', 'christian', 'episcopal', 'methodist', 'baptist', 'lutheran', 'parish', 'academy', 'preparatory', 'prep']):
        if 'district' not in name_lower:
            return 'private'
    
    if any(word in name_lower for word in ['charter', 'academy']) and 'district' not in name_lower:
        return 'charter'
    
    if any(word in name_lower for word in ['district', 'unified', 'school district', 'public']):
        return 'district'
    
    if 'cmo' in name_lower or 'charter management' in name_lower:
        return 'cmo'
    
    if 'esc' in name_lower or 'educational service' in name_lower:
        return 'esc'
    
    # Default classification
    if 'school' in name_lower:
        return 'charter'  # Default individual schools to charter
    else:
        return 'district'  # Default organizations to district

def main():
    print("🔄 Starting smart geocoding with deduplication...")
    
    # Load existing cache
    geocoded_cache = load_existing_cache()
    
    # Read the comprehensive file
    print(f"\n📁 Reading comprehensive client file...")
    df = pd.read_excel('MAP INFO - ALL CMS CLIENTS-2025-07-08-12-05-34.xlsx')
    print(f"Found {len(df)} total clients in new file")
    
    # Process each client
    customer_data = []
    new_geocodes = 0
    cache_hits = 0
    failed_geocodes = 0
    
    for index, row in df.iterrows():
        try:
            # Clean and format address
            address_parts = [
                row.get('Street Address', ''),
                row.get('City', ''),
                row.get('State', ''),
                row.get('Zip', '')
            ]
            
            full_address = clean_address(address_parts)
            
            if not full_address:
                print(f"Skipping row {index + 1}: No valid address")
                continue
            
            # Check if already geocoded
            location = None
            if full_address in geocoded_cache:
                location = geocoded_cache[full_address]
                cache_hits += 1
                print(f"[{index + 1}/{len(df)}] {row['School or District Name'][:50]}... - Using cached location")
            else:
                # Geocode new address
                print(f"[{index + 1}/{len(df)}] {row['School or District Name'][:50]}... - Geocoding...")
                location = geocode_address(full_address)
                
                if location:
                    geocoded_cache[full_address] = location
                    new_geocodes += 1
                    # Rate limiting for API
                    time.sleep(1)
                else:
                    failed_geocodes += 1
                    print(f"  ❌ Failed to geocode: {full_address}")
                    continue
            
            # Create customer entry
            if location:
                website = row.get('Website', '')
                if website and not website.startswith('http'):
                    website = f"https://{website}"
                
                customer = {
                    'name': str(row['School or District Name']),
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'url': website,
                    'type': determine_school_type(str(row['School or District Name'])),
                    'state': str(row.get('State', ''))
                }
                
                customer_data.append(customer)
            
            # Save progress every 50 addresses
            if (index + 1) % 50 == 0:
                save_progress(geocoded_cache, customer_data)
                print(f"  Progress saved. Cache hits: {cache_hits}, New geocodes: {new_geocodes}, Failed: {failed_geocodes}")
        
        except Exception as e:
            print(f"Error processing row {index + 1}: {e}")
            continue
    
    # Final save
    save_progress(geocoded_cache, customer_data)
    
    print(f"\n✅ Geocoding complete!")
    print(f"📊 Summary:")
    print(f"   • Total customers processed: {len(customer_data)}")
    print(f"   • Cache hits (saved API calls): {cache_hits}")
    print(f"   • New geocodes: {new_geocodes}")
    print(f"   • Failed geocodes: {failed_geocodes}")
    print(f"   • Total addresses in cache: {len(geocoded_cache)}")
    
    # Show type breakdown
    type_counts = {}
    for customer in customer_data:
        type_counts[customer['type']] = type_counts.get(customer['type'], 0) + 1
    
    print(f"\n📋 School type breakdown:")
    for school_type, count in sorted(type_counts.items()):
        print(f"   • {school_type.title()}: {count}")

if __name__ == "__main__":
    main()