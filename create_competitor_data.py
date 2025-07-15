#!/usr/bin/env python3
"""
Create competitor data structure for immediate testing
"""

import csv
import json
import random

def create_sample_competitor_data():
    """Create sample competitor data for immediate testing"""
    
    # Sample locations across US for testing
    sample_locations = [
        {"city": "Austin", "state": "Texas", "lat": 30.2672, "lng": -97.7431},
        {"city": "Dallas", "state": "Texas", "lat": 32.7767, "lng": -96.7970},
        {"city": "Houston", "state": "Texas", "lat": 29.7604, "lng": -95.3698},
        {"city": "Los Angeles", "state": "California", "lat": 34.0522, "lng": -118.2437},
        {"city": "San Francisco", "state": "California", "lat": 37.7749, "lng": -122.4194},
        {"city": "Miami", "state": "Florida", "lat": 25.7617, "lng": -80.1918},
        {"city": "Orlando", "state": "Florida", "lat": 28.5383, "lng": -81.3792},
        {"city": "New York", "state": "New York", "lat": 40.7128, "lng": -74.0060},
        {"city": "Chicago", "state": "Illinois", "lat": 41.8781, "lng": -87.6298},
        {"city": "Atlanta", "state": "Georgia", "lat": 33.7490, "lng": -84.3880},
        {"city": "Phoenix", "state": "Arizona", "lat": 33.4484, "lng": -112.0740},
        {"city": "Denver", "state": "Colorado", "lat": 39.7392, "lng": -104.9903},
        {"city": "Seattle", "state": "Washington", "lat": 47.6062, "lng": -122.3321},
        {"city": "Boston", "state": "Massachusetts", "lat": 42.3601, "lng": -71.0589},
        {"city": "Philadelphia", "state": "Pennsylvania", "lat": 39.9526, "lng": -75.1652}
    ]
    
    competitor_schools = []
    
    # Read first 50 rows from CSV for sample data
    with open('hubspot-crm-exports-all-apptegy-schools-2025-07-15.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i, row in enumerate(reader):
            if i >= 50:  # Just 50 for testing
                break
                
            company_name = row.get('Company name', '').strip()
            domain = row.get('Company Domain Name', '').strip()
            owner = row.get('Company owner', '').strip()
            create_date = row.get('Create Date', '').strip()
            
            if not company_name:
                continue
            
            # Randomly assign a location for testing
            location = random.choice(sample_locations)
            
            # Add some randomness to coordinates
            lat_offset = random.uniform(-0.1, 0.1)
            lng_offset = random.uniform(-0.1, 0.1)
            
            school_data = {
                'recordId': row.get('Record ID', ''),
                'name': company_name,
                'competitor': 'Apptegy',
                'domain': domain,
                'city': location['city'],
                'state': location['state'],
                'owner': owner,
                'createDate': create_date,
                'lat': location['lat'] + lat_offset,
                'lng': location['lng'] + lng_offset,
                'type': 'competitor',
                'products': ['CMS'],  # Apptegy is primarily CMS
                'customerType': 'District',  # Most are districts
                'arr': random.randint(5000, 50000),  # Estimated ARR
                'employees': random.randint(50, 5000),  # Estimated size
                'lastContact': create_date,
                'salesStage': 'Competitor',
                'priority': 'High'
            }
            
            competitor_schools.append(school_data)
    
    print(f"Created {len(competitor_schools)} sample competitor schools")
    
    # Save to JSON file
    with open('apptegy-competitor-data.json', 'w', encoding='utf-8') as f:
        json.dump(competitor_schools, f, indent=2, ensure_ascii=False)
    
    print("Saved to apptegy-competitor-data.json")
    
    return competitor_schools

if __name__ == "__main__":
    create_sample_competitor_data()