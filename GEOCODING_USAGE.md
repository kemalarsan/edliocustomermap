# Apptegy Schools Geocoding Usage Guide

## Overview
This script geocodes the remaining Apptegy schools from the CSV file using OpenStreetMap Nominatim API with proper rate limiting and resume capabilities.

## Files Created
- `geocode_apptegy_schools.py` - Main geocoding script
- `check_geocoding_status.py` - Status checker script
- `requirements.txt` - Python dependencies
- `GEOCODING_USAGE.md` - This usage guide

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the CSV file exists:
   - `hubspot-crm-exports-all-apptegy-schools-2025-07-15.csv`

## Running the Geocoder

### Basic Usage
```bash
python3 geocode_apptegy_schools.py
```

### Background Processing (Recommended)
```bash
nohup python3 geocode_apptegy_schools.py > geocoding_output.log 2>&1 &
```

## Checking Status

While the script is running (or to check completed results):
```bash
python3 check_geocoding_status.py
```

## Features

### Rate Limiting
- 1 second delay between API requests to respect Nominatim usage policy
- Exponential backoff on failures
- Maximum 3 retry attempts per address

### Resume Capability
- Progress is saved every 100 schools processed
- If interrupted, simply restart the script - it will resume from where it left off
- Progress file: `geocoding_progress.json`

### Batch Processing
- Processes schools in batches of 100
- Status updates every 10 schools
- Incremental saving to prevent data loss

### State Extraction
- Extracts state information from domain patterns (.tx.us, .k12.ca.us, etc.)
- Parses location from company names
- Uses existing city/zip data when available

### Error Handling
- Graceful handling of network failures
- Comprehensive logging to `geocoding.log`
- Failed attempts are saved separately for analysis

## Output Files

### `apptegy-geocoded-batch.json`
Final results file containing:
- Metadata (processing stats, timestamps)
- Successful geocodes with lat/lng coordinates
- Failed attempts with error reasons

### `geocoding_progress.json`
Progress tracking file containing:
- Last processed index
- Current results and errors
- Timestamp of last update

### `geocoding.log`
Detailed log file with:
- Processing status updates
- Error messages
- API response information

## Expected Processing Time

With ~12,700 remaining schools and 1-second rate limiting:
- Estimated time: ~3.5-4 hours
- Success rate typically 85-95% depending on data quality

## Monitoring Progress

The script provides regular status updates:
- Every 10 schools: Current progress and success rate
- Every 100 schools: Progress saved to disk
- Detailed logging for troubleshooting

## Interruption and Resume

The script can be safely interrupted (Ctrl+C) and will:
1. Save current progress
2. Exit gracefully
3. Resume from the last saved position when restarted

## Data Quality Notes

The script attempts to geocode using:
1. Company name + existing city + state (from domain)
2. Company name + extracted location from name
3. Fallback to company name + "school" + state

State extraction covers all US states via domain patterns like:
- `.k12.tx.us` → Texas
- `.ca.us` → California
- And many other variations

## Troubleshooting

### Common Issues
1. **Network timeouts**: Script includes retry logic
2. **Rate limiting**: Built-in delays prevent API blocking
3. **No results**: Often due to incomplete/unclear location data
4. **Memory usage**: Minimal - processes one record at a time

### Log Analysis
Check `geocoding.log` for detailed error information and processing statistics.

## Post-Processing

After completion, the `apptegy-geocoded-batch.json` file contains all results and can be:
- Imported into mapping applications
- Analyzed for success rates
- Combined with previous geocoding results
- Used for further data processing