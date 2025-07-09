#!/usr/bin/env python3
"""
Intelligent Autonomous Geocoding System
Designed to run unattended and process large datasets efficiently.
"""

import pandas as pd
import json
import requests
import time
import re
from datetime import datetime, timedelta
import os
import logging
import signal
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelligent_geocoding.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntelligentGeocoder:
    def __init__(self):
        self.cache_file = 'geocoded_data.json'
        self.output_file = 'data.js'
        self.batch_size = 20  # Process in small batches
        self.delay_between_requests = 1.5  # Conservative rate limiting
        self.delay_between_batches = 30  # 30 seconds between batches
        self.max_retries = 3
        self.should_stop = False
        
        # Set up graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🤖 Intelligent Geocoder initialized")
    
    def signal_handler(self, signum, frame):
        logger.info("🛑 Shutdown signal received. Finishing current batch...")
        self.should_stop = True
    
    def load_cache(self):
        """Load existing geocoded cache"""
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            logger.info(f"📂 Loaded {len(cache)} cached addresses")
            return cache
        except FileNotFoundError:
            logger.info("📂 No existing cache found, starting fresh")
            return {}
    
    def save_cache(self, cache):
        """Save geocoded cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    
    def clean_address(self, row):
        """Clean and format address for geocoding"""
        # Handle the new file format where columns are mixed up
        parts = []
        
        # Try to reconstruct proper address from mixed columns
        street = str(row.get('STATE', '')).strip()  # STATE column has street address
        city = str(row.get('Street Address', '')).strip()  # Street Address has city
        state = str(row.get('City Address', '')).strip()  # City Address has state
        zip_code = str(row.get('Zip Address', '')).strip()  # Zip Address has zip
        
        # Add non-empty parts
        for part in [street, city, state, zip_code]:
            if part and part != 'nan' and part != 'None':
                parts.append(part)
        
        full_address = ', '.join(parts)
        
        # Clean up
        full_address = re.sub(r'\s+', ' ', full_address)
        full_address = re.sub(r',\s*,', ',', full_address)
        full_address = full_address.strip(', ')
        
        return full_address
    
    def geocode_address(self, address):
        """Geocode an address with retry logic"""
        for attempt in range(self.max_retries):
            try:
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': address,
                    'format': 'json',
                    'limit': 1,
                    'addressdetails': 1
                }
                headers = {
                    'User-Agent': 'EdlioCustomerMap/2.0 (intelligent-geocoding)'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=15)
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
                logger.warning(f"  Attempt {attempt + 1} failed for {address[:50]}... Error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        return None
    
    def determine_school_type(self, name, institution_type=None, building_charter=None):
        """Determine school type based on name and additional fields"""
        name_lower = name.lower()
        
        # Check institution type first
        if institution_type and 'charter' in str(institution_type).lower():
            return 'charter'
        
        # Check building charter field
        if building_charter and pd.notna(building_charter):
            if 'charter' in str(building_charter).lower():
                return 'charter'
        
        # Private school indicators
        if any(word in name_lower for word in ['catholic', 'christian', 'episcopal', 'methodist', 'baptist', 'lutheran', 'parish', 'academy', 'preparatory', 'prep']):
            if 'district' not in name_lower:
                return 'private'
        
        # Charter school indicators
        if any(word in name_lower for word in ['charter', 'academy']) and 'district' not in name_lower:
            return 'charter'
        
        # District indicators
        if any(word in name_lower for word in ['district', 'unified', 'school district', 'public']):
            return 'district'
        
        # CMO indicators
        if 'cmo' in name_lower or 'charter management' in name_lower:
            return 'cmo'
        
        # ESC indicators
        if 'esc' in name_lower or 'educational service' in name_lower:
            return 'esc'
        
        # Default classification
        if 'school' in name_lower:
            return 'charter'
        else:
            return 'district'
    
    def load_and_combine_data(self):
        """Load and combine data from all Excel files"""
        logger.info("📊 Loading and combining data sources...")
        
        # Load the updated file with product data
        df_updated = pd.read_excel('UPDATED - MAP INFO - ALL CLIENTS-2025-07-08-16-18-18.xlsx')
        logger.info(f"📁 Loaded {len(df_updated)} customers from UPDATED file")
        
        combined_customers = []
        seen_names = set()
        
        for _, row in df_updated.iterrows():
            try:
                name = str(row['School Name']).strip()
                
                # Skip duplicates
                if name.lower() in seen_names:
                    continue
                seen_names.add(name.lower())
                
                # Clean website URL
                website = str(row.get('Website', '')).strip()
                if website and not website.startswith('http'):
                    website = f"https://{website}"
                
                # Extract state from proper column
                state = str(row.get('City Address', '')).strip()
                
                customer = {
                    'name': name,
                    'address': self.clean_address(row),
                    'website': website,
                    'state': state,
                    'type': self.determine_school_type(
                        name, 
                        row.get('Agile Institution Type'),
                        row.get('Agile Building Charter')
                    ),
                    'products': {
                        'cms': bool(row.get('CMS', False)),
                        'mobile': bool(row.get('Access', False)),  # Access appears to be mobile
                        'masscomm': bool(row.get('SIA', False)),   # SIA appears to be communications
                        'payments': bool(row.get('Pay', False))
                    }
                }
                
                if customer['address']:  # Only add if we have an address to geocode
                    combined_customers.append(customer)
                
            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                continue
        
        logger.info(f"✅ Combined {len(combined_customers)} unique customers with product data")
        return combined_customers
    
    def save_progress(self, customers, cache):
        """Save current progress to data.js"""
        try:
            with open(self.output_file, 'w') as f:
                f.write("// Real Edlio customer data with product information\n")
                f.write(f"// Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"// Total customers: {len(customers)}\n")
                f.write("const customers = [\n")
                
                for customer in customers:
                    if customer.get('lat') and customer.get('lng'):
                        products_str = json.dumps(customer['products'])
                        f.write(f'    {{ name: "{customer["name"]}", '
                               f'lat: {customer["lat"]}, '
                               f'lng: {customer["lng"]}, '
                               f'url: "{customer["website"]}", '
                               f'type: "{customer["type"]}", '
                               f'state: "{customer["state"]}", '
                               f'products: {products_str} }},\n')
                
                f.write("];\n")
            
            # Save cache
            self.save_cache(cache)
            logger.info(f"💾 Progress saved: {len([c for c in customers if c.get('lat')])} geocoded customers")
            
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def run_intelligent_geocoding(self):
        """Run the intelligent geocoding process"""
        logger.info("🚀 Starting intelligent geocoding process...")
        
        # Load data and cache
        customers = self.load_and_combine_data()
        cache = self.load_cache()
        
        # Statistics
        total_customers = len(customers)
        geocoded_count = 0
        cache_hits = 0
        failed_count = 0
        batch_count = 0
        
        logger.info(f"📊 Processing {total_customers} customers in batches of {self.batch_size}")
        
        for i in range(0, total_customers, self.batch_size):
            if self.should_stop:
                logger.info("🛑 Stopping due to shutdown signal")
                break
            
            batch = customers[i:i + self.batch_size]
            batch_count += 1
            
            logger.info(f"🔄 Processing batch {batch_count} ({i+1}-{min(i+self.batch_size, total_customers)} of {total_customers})")
            
            batch_processed = 0
            for customer in batch:
                if self.should_stop:
                    break
                
                address = customer['address']
                
                # Check cache first
                if address in cache:
                    customer.update(cache[address])
                    cache_hits += 1
                    geocoded_count += 1
                else:
                    # Geocode new address
                    logger.info(f"  🌍 Geocoding: {customer['name'][:50]}...")
                    location = self.geocode_address(address)
                    
                    if location:
                        customer.update(location)
                        cache[address] = location
                        geocoded_count += 1
                        logger.info(f"    ✅ Success: {location['lat']:.4f}, {location['lng']:.4f}")
                    else:
                        failed_count += 1
                        logger.warning(f"    ❌ Failed to geocode: {address}")
                        continue
                    
                    # Rate limiting
                    time.sleep(self.delay_between_requests)
                
                batch_processed += 1
            
            # Save progress after each batch
            self.save_progress(customers, cache)
            
            # Report progress
            logger.info(f"📊 Batch {batch_count} complete: {batch_processed} processed")
            logger.info(f"📈 Total progress: {geocoded_count}/{total_customers} ({geocoded_count/total_customers*100:.1f}%)")
            logger.info(f"💾 Cache hits: {cache_hits}, New geocodes: {geocoded_count-cache_hits}, Failed: {failed_count}")
            
            # Rest between batches (unless it's the last batch)
            if i + self.batch_size < total_customers and not self.should_stop:
                logger.info(f"😴 Resting {self.delay_between_batches} seconds before next batch...")
                time.sleep(self.delay_between_batches)
        
        # Final save and report
        self.save_progress(customers, cache)
        
        logger.info("🎉 Geocoding process complete!")
        logger.info(f"📊 Final Statistics:")
        logger.info(f"   • Total customers: {total_customers}")
        logger.info(f"   • Successfully geocoded: {geocoded_count}")
        logger.info(f"   • Cache hits: {cache_hits}")
        logger.info(f"   • New geocodes: {geocoded_count - cache_hits}")
        logger.info(f"   • Failed: {failed_count}")
        logger.info(f"   • Success rate: {geocoded_count/total_customers*100:.1f}%")

def main():
    geocoder = IntelligentGeocoder()
    geocoder.run_intelligent_geocoding()

if __name__ == "__main__":
    main()