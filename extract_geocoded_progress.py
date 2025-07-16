#!/usr/bin/env python3
"""
Extract successfully geocoded schools from the progress file
"""

import json
import os

def extract_geocoded_schools():
    """Extract successfully geocoded schools from progress"""
    
    # Read the current progress
    if not os.path.exists('geocoding_progress.json'):
        print("No progress file found")
        return
    
    with open('geocoding_progress.json', 'r') as f:
        progress = json.load(f)
    
    # Extract successfully geocoded schools from results
    successful_geocodes = []
    
    for result in progress.get('results', []):
        if result.get('geocoded') and result.get('location'):
            location = result['location']
            address = location.get('address', {})
            
            # Create competitor data structure
            school_data = {
                'recordId': result.get('record_id', ''),
                'name': result.get('company_name', ''),
                'competitor': 'Apptegy',
                'domain': '',  # Will be filled from original CSV later
                'city': address.get('city') or address.get('town') or address.get('village') or '',
                'state': address.get('state') or '',
                'owner': '',  # Will be filled from original CSV later
                'createDate': result.get('processed_at', ''),
                'lat': location.get('latitude'),
                'lng': location.get('longitude'),
                'displayName': location.get('display_name', ''),
                'type': 'competitor'
            }
            
            successful_geocodes.append(school_data)
    
    print(f"Found {len(successful_geocodes)} successfully geocoded schools")
    
    # Combine with the original 50 demo schools
    all_geocoded = []
    
    # First add the original demo data
    if os.path.exists('apptegy-competitor-data.json'):
        with open('apptegy-competitor-data.json', 'r') as f:
            demo_data = json.load(f)
            all_geocoded.extend(demo_data)
            print(f"Added {len(demo_data)} demo schools")
    
    # Add the new geocoded schools
    all_geocoded.extend(successful_geocodes)
    
    # Save to new file
    output_file = 'apptegy-geocoded-current.json'
    with open(output_file, 'w') as f:
        json.dump(all_geocoded, f, indent=2)
    
    print(f"Total schools saved: {len(all_geocoded)}")
    print(f"Saved to: {output_file}")
    
    # Generate summary statistics
    states = {}
    cities = {}
    
    for school in all_geocoded:
        state = school.get('state', 'Unknown')
        city = school.get('city', 'Unknown')
        
        states[state] = states.get(state, 0) + 1
        cities[f"{city}, {state}"] = cities.get(f"{city}, {state}", 0) + 1
    
    print("\nTop 10 states:")
    for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {state}: {count} schools")
    
    print("\nTop 10 cities:")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {city}: {count} schools")

if __name__ == "__main__":
    extract_geocoded_schools()