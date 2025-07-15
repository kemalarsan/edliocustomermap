#!/usr/bin/env python3
"""
Process Apptegy competitor data from HubSpot CRM export
Geocode schools and prepare for competitive analysis
"""

import csv
import json
import requests
import time
from collections import defaultdict
import re

def clean_location_data(row):
    """Extract and clean location information from the row"""
    # Try to get city from various columns
    city = row.get('City', '').strip()
    if not city:
        city = row.get('Agile Location City', '').strip()
    
    # Try to get state from company name or domain
    company_name = row.get('Company name', '').strip()
    domain = row.get('Company Domain Name', '').strip()
    
    # Common state abbreviations in school names
    state_patterns = {
        'TX': 'Texas', 'CA': 'California', 'FL': 'Florida', 'NY': 'New York',
        'IL': 'Illinois', 'PA': 'Pennsylvania', 'OH': 'Ohio', 'MI': 'Michigan',
        'GA': 'Georgia', 'NC': 'North Carolina', 'VA': 'Virginia', 'WA': 'Washington',
        'AZ': 'Arizona', 'MA': 'Massachusetts', 'IN': 'Indiana', 'TN': 'Tennessee',
        'MO': 'Missouri', 'MD': 'Maryland', 'WI': 'Wisconsin', 'CO': 'Colorado',
        'MN': 'Minnesota', 'SC': 'South Carolina', 'AL': 'Alabama', 'LA': 'Louisiana',
        'KY': 'Kentucky', 'OR': 'Oregon', 'OK': 'Oklahoma', 'CT': 'Connecticut',
        'IA': 'Iowa', 'MS': 'Mississippi', 'AR': 'Arkansas', 'KS': 'Kansas',
        'UT': 'Utah', 'NV': 'Nevada', 'NM': 'New Mexico', 'NE': 'Nebraska',
        'WV': 'West Virginia', 'ID': 'Idaho', 'HI': 'Hawaii', 'NH': 'New Hampshire',
        'ME': 'Maine', 'RI': 'Rhode Island', 'MT': 'Montana', 'DE': 'Delaware',
        'SD': 'South Dakota', 'ND': 'North Dakota', 'AK': 'Alaska', 'VT': 'Vermont',
        'WY': 'Wyoming'
    }
    
    state = ''
    # Try to extract state from domain (e.g., .tx.us, .ca.us, .k12.fl.us)
    if domain:
        for abbr, full_name in state_patterns.items():
            if f'.{abbr.lower()}.' in domain.lower() or f'.k12.{abbr.lower()}.' in domain.lower():
                state = full_name
                break
    
    # If no state found, try to infer from company name patterns
    if not state:
        name_lower = company_name.lower()
        for abbr, full_name in state_patterns.items():
            if f' {abbr.lower()} ' in name_lower or name_lower.endswith(f' {abbr.lower()}'):
                state = full_name
                break
    
    return city, state

def geocode_school(company_name, city, state, domain):
    """Geocode a school using OpenStreetMap Nominatim"""
    try:
        # Build search query
        query_parts = []
        if company_name:
            query_parts.append(company_name)
        if city:
            query_parts.append(city)
        if state:
            query_parts.append(state)
        
        query = ', '.join(query_parts)
        
        # OpenStreetMap Nominatim API
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'EdlioCompetitorAnalysis/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = data[0]
                return {
                    'lat': float(result['lat']),
                    'lng': float(result['lon']),
                    'display_name': result.get('display_name', ''),
                    'geocoded': True
                }
        
        return None
        
    except Exception as e:
        print(f"Geocoding error for {company_name}: {e}")
        return None

def process_apptegy_data():
    """Process the Apptegy CSV file and create competitor data"""
    
    print("Processing Apptegy competitor data...")
    
    competitor_schools = []
    geocoded_count = 0
    
    # Read the CSV file
    with open('hubspot-crm-exports-all-apptegy-schools-2025-07-15.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i, row in enumerate(reader):
            if i >= 100:  # Limit for testing - remove this for full processing
                break
                
            company_name = row.get('Company name', '').strip()
            domain = row.get('Company Domain Name', '').strip()
            owner = row.get('Company owner', '').strip()
            create_date = row.get('Create Date', '').strip()
            
            if not company_name:
                continue
            
            # Clean location data
            city, state = clean_location_data(row)
            
            # Geocode the school
            location = geocode_school(company_name, city, state, domain)
            
            if location:
                geocoded_count += 1
                
                school_data = {
                    'recordId': row.get('Record ID', ''),
                    'name': company_name,
                    'competitor': 'Apptegy',
                    'domain': domain,
                    'city': city,
                    'state': state,
                    'owner': owner,
                    'createDate': create_date,
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'displayName': location['display_name'],
                    'type': 'competitor'
                }
                
                competitor_schools.append(school_data)
                
                print(f"Geocoded {geocoded_count}: {company_name} in {city}, {state}")
                
                # Rate limiting for API
                time.sleep(1)
            
            else:
                print(f"Failed to geocode: {company_name}")
    
    print(f"\\nProcessed {len(competitor_schools)} Apptegy schools successfully")
    
    # Save to JSON file
    with open('apptegy-competitor-data.json', 'w', encoding='utf-8') as f:
        json.dump(competitor_schools, f, indent=2, ensure_ascii=False)
    
    print(f"Saved competitor data to apptegy-competitor-data.json")
    
    # Generate summary stats
    states = defaultdict(int)
    for school in competitor_schools:
        if school['state']:
            states[school['state']] += 1
    
    print("\\nTop states by Apptegy presence:")
    for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {state}: {count} schools")

if __name__ == "__main__":
    process_apptegy_data()