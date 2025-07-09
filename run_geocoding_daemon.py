#!/usr/bin/env python3
"""
Autonomous Geocoding Daemon
Runs geocoding intelligently during off-hours with automatic scheduling.
"""

import subprocess
import time
import logging
from datetime import datetime, time as dt_time
import signal
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('geocoding_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GeocodingDaemon:
    def __init__(self):
        self.should_stop = False
        self.geocoding_process = None
        
        # Configure optimal hours (adjust as needed)
        self.start_hour = 22  # 10 PM
        self.end_hour = 6     # 6 AM
        
        # Set up graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🌙 Geocoding Daemon initialized")
        logger.info(f"⏰ Will run during off-hours: {self.start_hour}:00 - {self.end_hour}:00")
    
    def signal_handler(self, signum, frame):
        logger.info("🛑 Daemon shutdown signal received")
        self.should_stop = True
        if self.geocoding_process:
            logger.info("⏹️ Terminating geocoding process...")
            self.geocoding_process.terminate()
    
    def is_off_hours(self):
        """Check if current time is during off-hours"""
        current_hour = datetime.now().hour
        
        if self.start_hour > self.end_hour:  # Spans midnight
            return current_hour >= self.start_hour or current_hour < self.end_hour
        else:  # Same day
            return self.start_hour <= current_hour < self.end_hour
    
    def run_geocoding(self):
        """Run the geocoding process"""
        try:
            logger.info("🚀 Starting geocoding process...")
            
            # Run the intelligent geocoder
            self.geocoding_process = subprocess.Popen(
                ['python3', 'intelligent_geocoder.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=os.getcwd()
            )
            
            # Monitor the process
            while True:
                output = self.geocoding_process.stdout.readline()
                if output == '' and self.geocoding_process.poll() is not None:
                    break
                if output:
                    logger.info(f"📍 {output.strip()}")
                
                # Check if we should stop
                if self.should_stop or not self.is_off_hours():
                    logger.info("⏰ Off-hours ended or stop requested, terminating...")
                    self.geocoding_process.terminate()
                    break
            
            # Get final return code
            return_code = self.geocoding_process.wait()
            logger.info(f"✅ Geocoding process finished with code: {return_code}")
            
        except Exception as e:
            logger.error(f"❌ Error running geocoding: {e}")
        finally:
            self.geocoding_process = None
    
    def run_daemon(self):
        """Main daemon loop"""
        logger.info("🎯 Geocoding daemon started")
        
        while not self.should_stop:
            try:
                if self.is_off_hours():
                    logger.info("🌙 Off-hours detected, starting geocoding...")
                    self.run_geocoding()
                    
                    if not self.should_stop:
                        logger.info("💤 Geocoding complete, waiting until next off-hours period...")
                else:
                    logger.info("☀️ Business hours, waiting...")
                
                # Wait 30 minutes before checking again
                for _ in range(1800):  # 30 minutes in seconds
                    if self.should_stop:
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"❌ Daemon error: {e}")
                time.sleep(60)  # Wait 1 minute on error
        
        logger.info("👋 Geocoding daemon stopped")

def main():
    """Run the daemon or geocoding directly based on command line args"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--now':
            # Run geocoding immediately
            logger.info("🚀 Running geocoding immediately...")
            from intelligent_geocoder import IntelligentGeocoder
            geocoder = IntelligentGeocoder()
            geocoder.run_intelligent_geocoding()
        elif sys.argv[1] == '--test':
            # Test the current data without geocoding
            logger.info("🧪 Testing data combination...")
            from intelligent_geocoder import IntelligentGeocoder
            geocoder = IntelligentGeocoder()
            customers = geocoder.load_and_combine_data()
            
            # Show product statistics
            product_stats = {'cms': 0, 'mobile': 0, 'masscomm': 0, 'payments': 0}
            for customer in customers:
                for product, has_it in customer['products'].items():
                    if has_it:
                        product_stats[product] += 1
            
            logger.info(f"📊 Product Statistics:")
            logger.info(f"   • CMS: {product_stats['cms']}")
            logger.info(f"   • Mobile/Access: {product_stats['mobile']}")
            logger.info(f"   • Mass Communications: {product_stats['masscomm']}")
            logger.info(f"   • Payments: {product_stats['payments']}")
    else:
        # Run as daemon
        daemon = GeocodingDaemon()
        daemon.run_daemon()

if __name__ == "__main__":
    main()