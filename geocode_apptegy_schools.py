#!/usr/bin/env python3
"""
Apptegy Schools Geocoding Script

This script geocodes Apptegy schools from a CSV file using OpenStreetMap Nominatim.
Features:
- Batch processing with rate limiting
- Resume capability from interruption
- Progress tracking and logging
- Error handling and retry logic
- State extraction from domains and names
"""

import csv
import json
import time
import re
import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
import signal
import sys

# Configuration
CSV_FILE = "hubspot-crm-exports-all-apptegy-schools-2025-07-15.csv"
OUTPUT_FILE = "apptegy-geocoded-batch.json"
PROGRESS_FILE = "geocoding_progress.json"
LOG_FILE = "geocoding.log"

SKIP_ROWS = 50  # Skip first 50 already processed rows
BATCH_SIZE = 100
RATE_LIMIT_DELAY = 1.0  # 1 second between requests
STATUS_UPDATE_INTERVAL = 10
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# State mapping for common domain patterns
STATE_MAPPING = {
    '.k12.al.us': 'Alabama', '.k12.ak.us': 'Alaska', '.k12.az.us': 'Arizona',
    '.k12.ar.us': 'Arkansas', '.k12.ca.us': 'California', '.k12.co.us': 'Colorado',
    '.k12.ct.us': 'Connecticut', '.k12.de.us': 'Delaware', '.k12.fl.us': 'Florida',
    '.k12.ga.us': 'Georgia', '.k12.hi.us': 'Hawaii', '.k12.id.us': 'Idaho',
    '.k12.il.us': 'Illinois', '.k12.in.us': 'Indiana', '.k12.ia.us': 'Iowa',
    '.k12.ks.us': 'Kansas', '.k12.ky.us': 'Kentucky', '.k12.la.us': 'Louisiana',
    '.k12.me.us': 'Maine', '.k12.md.us': 'Maryland', '.k12.ma.us': 'Massachusetts',
    '.k12.mi.us': 'Michigan', '.k12.mn.us': 'Minnesota', '.k12.ms.us': 'Mississippi',
    '.k12.mo.us': 'Missouri', '.k12.mt.us': 'Montana', '.k12.ne.us': 'Nebraska',
    '.k12.nv.us': 'Nevada', '.k12.nh.us': 'New Hampshire', '.k12.nj.us': 'New Jersey',
    '.k12.nm.us': 'New Mexico', '.k12.ny.us': 'New York', '.k12.nc.us': 'North Carolina',
    '.k12.nd.us': 'North Dakota', '.k12.oh.us': 'Ohio', '.k12.ok.us': 'Oklahoma',
    '.k12.or.us': 'Oregon', '.k12.pa.us': 'Pennsylvania', '.k12.ri.us': 'Rhode Island',
    '.k12.sc.us': 'South Carolina', '.k12.sd.us': 'South Dakota', '.k12.tn.us': 'Tennessee',
    '.k12.tx.us': 'Texas', '.k12.ut.us': 'Utah', '.k12.vt.us': 'Vermont',
    '.k12.va.us': 'Virginia', '.k12.wa.us': 'Washington', '.k12.wv.us': 'West Virginia',
    '.k12.wi.us': 'Wisconsin', '.k12.wy.us': 'Wyoming',
    # Additional state patterns
    '.tx.us': 'Texas', '.ca.us': 'California', '.ny.us': 'New York',
    '.fl.us': 'Florida', '.il.us': 'Illinois', '.pa.us': 'Pennsylvania',
    '.oh.us': 'Ohio', '.ga.us': 'Georgia', '.nc.us': 'North Carolina',
    '.mi.us': 'Michigan', '.nj.us': 'New Jersey', '.va.us': 'Virginia',
    '.wa.us': 'Washington', '.az.us': 'Arizona', '.ma.us': 'Massachusetts',
    '.tn.us': 'Tennessee', '.in.us': 'Indiana', '.mo.us': 'Missouri',
    '.md.us': 'Maryland', '.wi.us': 'Wisconsin', '.co.us': 'Colorado',
    '.mn.us': 'Minnesota', '.sc.us': 'South Carolina', '.al.us': 'Alabama',
    '.la.us': 'Louisiana', '.ky.us': 'Kentucky', '.or.us': 'Oregon',
    '.ok.us': 'Oklahoma', '.ct.us': 'Connecticut', '.ut.us': 'Utah',
    '.ia.us': 'Iowa', '.nv.us': 'Nevada', '.ar.us': 'Arkansas',
    '.ms.us': 'Mississippi', '.ks.us': 'Kansas', '.nm.us': 'New Mexico',
    '.ne.us': 'Nebraska', '.wv.us': 'West Virginia', '.id.us': 'Idaho',
    '.nh.us': 'New Hampshire', '.me.us': 'Maine', '.ri.us': 'Rhode Island',
    '.mt.us': 'Montana', '.de.us': 'Delaware', '.sd.us': 'South Dakota',
    '.nd.us': 'North Dakota', '.ak.us': 'Alaska', '.vt.us': 'Vermont',
    '.wy.us': 'Wyoming', '.hi.us': 'Hawaii'
}

class GeocodingProgress:
    """Handles progress tracking and resume functionality"""
    
    def __init__(self, progress_file: str):
        self.progress_file = progress_file
        self.last_processed_index = SKIP_ROWS
        self.results = []
        self.errors = []
        self.load_progress()
    
    def load_progress(self):
        """Load existing progress if available"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.last_processed_index = data.get('last_processed_index', SKIP_ROWS)
                    self.results = data.get('results', [])
                    self.errors = data.get('errors', [])
                    logging.info(f"Resumed from index {self.last_processed_index}, "
                               f"with {len(self.results)} existing results and {len(self.errors)} errors")
            except Exception as e:
                logging.error(f"Error loading progress: {e}")
    
    def save_progress(self):
        """Save current progress to file"""
        try:
            progress_data = {
                'last_processed_index': self.last_processed_index,
                'results': self.results,
                'errors': self.errors,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving progress: {e}")

class SchoolGeocoder:
    """Main geocoding class for Apptegy schools"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Apptegy School Geocoder (educational research)'
        })
        self.progress = GeocodingProgress(PROGRESS_FILE)
        self.interrupted = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interruption signals gracefully"""
        logging.info(f"Received signal {signum}, saving progress and shutting down...")
        self.interrupted = True
        self.progress.save_progress()
        sys.exit(0)
    
    def extract_state_from_domain(self, domain: str) -> Optional[str]:
        """Extract state from domain name"""
        if not domain:
            return None
        
        domain_lower = domain.lower()
        for pattern, state in STATE_MAPPING.items():
            if pattern in domain_lower:
                return state
        return None
    
    def extract_location_from_name(self, name: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract city and state from company name"""
        if not name:
            return None, None
        
        # Common patterns for school names with locations
        patterns = [
            r'([A-Za-z\s]+)\s+(?:School District|ISD|USD|CSD)\s*(?:of\s+)?([A-Za-z\s]+)(?:,\s*([A-Z]{2}))?',
            r'([A-Za-z\s]+)\s+(?:Elementary|Middle|High|Schools?)\s*,?\s*([A-Za-z\s]+)(?:,\s*([A-Z]{2}))?',
            r'([A-Za-z\s]+)\s+(?:County|Parish)\s+(?:School District|Schools)',
            r'City of ([A-Za-z\s]+)\s+(?:School District|Schools)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    city = groups[1].strip() if groups[1] else groups[0].strip()
                    state = groups[2].strip() if len(groups) > 2 and groups[2] else None
                    return city, state
        
        return None, None
    
    def infer_state_from_city(self, city: str) -> Optional[str]:
        """Infer state from well-known cities"""
        if not city:
            return None
        
        # Common city -> state mappings for disambiguation
        city_state_map = {
            'euclid': 'Ohio',
            'cleveland': 'Ohio',
            'columbus': 'Ohio',
            'cincinnati': 'Ohio',
            'toledo': 'Ohio',
            'akron': 'Ohio',
            'dayton': 'Ohio',
            'houston': 'Texas',
            'dallas': 'Texas',
            'austin': 'Texas',
            'san antonio': 'Texas',
            'fort worth': 'Texas',
            'los angeles': 'California',
            'san francisco': 'California',
            'san diego': 'California',
            'sacramento': 'California',
            'fresno': 'California',
            'chicago': 'Illinois',
            'springfield': 'Illinois',
            'peoria': 'Illinois',
            'rockford': 'Illinois',
            'phoenix': 'Arizona',
            'tucson': 'Arizona',
            'mesa': 'Arizona',
            'atlanta': 'Georgia',
            'savannah': 'Georgia',
            'augusta': 'Georgia',
            'miami': 'Florida',
            'tampa': 'Florida',
            'orlando': 'Florida',
            'jacksonville': 'Florida',
            'tallahassee': 'Florida'
        }
        
        city_lower = city.lower().strip()
        return city_state_map.get(city_lower)
    
    def build_search_query(self, school_data: Dict) -> str:
        """Build search query from available school data"""
        query_parts = []
        
        # Start with company name
        company_name = school_data.get('Company name', '').strip()
        if company_name:
            # Clean up the company name for better geocoding
            cleaned_name = re.sub(r'\(.*?\)', '', company_name)  # Remove parentheses content
            cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()  # Normalize whitespace
            query_parts.append(cleaned_name)
        
        # Add city if available
        city = school_data.get('City', '').strip() or school_data.get('Agile Location City', '').strip()
        if city:
            query_parts.append(city)
        
        # Extract location from name if no city provided
        if not city:
            extracted_city, extracted_state = self.extract_location_from_name(company_name)
            if extracted_city:
                city = extracted_city
                query_parts.append(city)
        
        # Add state from multiple sources
        domain = school_data.get('Company Domain Name', '').strip()
        state = self.extract_state_from_domain(domain)
        
        # If no state from domain, try extracting from name
        if not state:
            _, extracted_state = self.extract_location_from_name(company_name)
            state = extracted_state
        
        # If still no state, try inferring from city
        if not state and city:
            state = self.infer_state_from_city(city)
        
        if state:
            query_parts.append(state)
        
        # Add "school" to help with disambiguation
        query_parts.append("school")
        
        return ", ".join(query_parts)
    
    def geocode_address(self, query: str) -> Optional[Dict]:
        """Geocode an address using Nominatim with fallback queries"""
        url = "https://nominatim.openstreetmap.org/search"
        
        # Try multiple query variations
        query_variations = [
            query,  # Original query
            query.replace(", school", ""),  # Remove trailing "school"
            query.replace(" school", "")    # Remove any "school" word
        ]
        
        for query_variant in query_variations:
            if not query_variant.strip():
                continue
                
            params = {
                'q': query_variant,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'dedupe': 1
            }
            
            for attempt in range(MAX_RETRIES):
                try:
                    time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
                    response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data:
                        result = data[0]
                        return {
                            'latitude': float(result['lat']),
                            'longitude': float(result['lon']),
                            'display_name': result['display_name'],
                            'address': result.get('address', {}),
                            'importance': result.get('importance', 0),
                            'place_id': result.get('place_id'),
                            'query_used': query_variant
                        }
                    else:
                        logging.warning(f"No results for query: {query_variant}")
                        break  # Try next variation
                        
                except requests.exceptions.RequestException as e:
                    logging.warning(f"Attempt {attempt + 1} failed for query '{query_variant}': {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        logging.error(f"All attempts failed for query: {query_variant}")
                        break  # Try next variation
                except Exception as e:
                    logging.error(f"Unexpected error geocoding '{query_variant}': {e}")
                    break  # Try next variation
        
        return None
    
    def process_school(self, school_data: Dict, index: int) -> Dict:
        """Process a single school record"""
        record_id = school_data.get('Record ID', '')
        company_name = school_data.get('Company name', '')
        
        result = {
            'record_id': record_id,
            'company_name': company_name,
            'index': index,
            'processed_at': datetime.now().isoformat(),
            'geocoded': False,
            'error': None,
            'location': None,
            'domain': school_data.get('Company Domain Name', ''),
            'existing_city': school_data.get('City', '') or school_data.get('Agile Location City', ''),
            'existing_zip': school_data.get('Agile Location Zip', '')
        }
        
        try:
            # Build search query
            query = self.build_search_query(school_data)
            if not query or len(query.strip()) < 5:
                result['error'] = "Insufficient data to build search query"
                return result
            
            # Attempt geocoding
            location = self.geocode_address(query)
            if location:
                result['geocoded'] = True
                result['location'] = location
                logging.info(f"Successfully geocoded: {company_name} -> {location['display_name']}")
            else:
                result['error'] = "No geocoding results found"
                
        except Exception as e:
            result['error'] = str(e)
            logging.error(f"Error processing school {record_id}: {e}")
        
        return result
    
    def load_csv_data(self) -> List[Dict]:
        """Load school data from CSV file"""
        schools = []
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= self.progress.last_processed_index:
                        schools.append(row)
        except Exception as e:
            logging.error(f"Error loading CSV data: {e}")
            raise
        
        return schools
    
    def run(self):
        """Main execution method"""
        logging.info("Starting Apptegy schools geocoding process")
        logging.info(f"Skipping first {SKIP_ROWS} rows, resuming from index {self.progress.last_processed_index}")
        
        # Load school data
        schools = self.load_csv_data()
        total_schools = len(schools)
        
        if total_schools == 0:
            logging.info("No schools to process")
            return
        
        logging.info(f"Loaded {total_schools} schools to process")
        
        # Process schools in batches
        processed_count = 0
        
        for i, school in enumerate(schools):
            if self.interrupted:
                break
            
            current_index = self.progress.last_processed_index + i
            
            # Process school
            result = self.process_school(school, current_index)
            
            if result['geocoded']:
                self.progress.results.append(result)
            else:
                self.progress.errors.append(result)
            
            processed_count += 1
            self.progress.last_processed_index = current_index + 1
            
            # Status update
            if processed_count % STATUS_UPDATE_INTERVAL == 0:
                success_rate = len(self.progress.results) / (len(self.progress.results) + len(self.progress.errors)) * 100
                logging.info(f"Processed {processed_count}/{total_schools} schools. "
                           f"Success rate: {success_rate:.1f}% "
                           f"({len(self.progress.results)} successful, {len(self.progress.errors)} failed)")
            
            # Save progress every batch
            if processed_count % BATCH_SIZE == 0:
                self.progress.save_progress()
                logging.info(f"Progress saved after processing {processed_count} schools")
        
        # Final save
        self.progress.save_progress()
        self.save_final_results()
        
        # Final statistics
        total_processed = len(self.progress.results) + len(self.progress.errors)
        success_rate = len(self.progress.results) / total_processed * 100 if total_processed > 0 else 0
        
        logging.info(f"Geocoding completed!")
        logging.info(f"Total processed: {total_processed}")
        logging.info(f"Successful: {len(self.progress.results)}")
        logging.info(f"Failed: {len(self.progress.errors)}")
        logging.info(f"Success rate: {success_rate:.1f}%")
    
    def save_final_results(self):
        """Save final results to output file"""
        try:
            output_data = {
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_results': len(self.progress.results),
                    'total_errors': len(self.progress.errors),
                    'success_rate': len(self.progress.results) / (len(self.progress.results) + len(self.progress.errors)) * 100,
                    'skipped_rows': SKIP_ROWS,
                    'last_processed_index': self.progress.last_processed_index
                },
                'successful_geocodes': self.progress.results,
                'failed_geocodes': self.progress.errors
            }
            
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logging.info(f"Final results saved to {OUTPUT_FILE}")
            
        except Exception as e:
            logging.error(f"Error saving final results: {e}")

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main entry point"""
    setup_logging()
    
    # Check if CSV file exists
    if not os.path.exists(CSV_FILE):
        logging.error(f"CSV file not found: {CSV_FILE}")
        sys.exit(1)
    
    geocoder = SchoolGeocoder()
    try:
        geocoder.run()
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
        geocoder.progress.save_progress()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        geocoder.progress.save_progress()
        sys.exit(1)

if __name__ == "__main__":
    main()