import threading
import time
import requests
import logging
from datetime import datetime
from app import app, db
from models import Website, MonitoringResult, MonitoringSettings

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        self.running = False
        self.thread = None
        self.check_interval = 30  # seconds
    
    def get_check_interval(self):
        """Get current check interval from database settings"""
        with app.app_context():
            settings = MonitoringSettings.query.first()
            if settings:
                return settings.check_interval
            return 30  # default fallback
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.thread.start()
        logger.info("Monitoring service started")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Monitoring service stopped")
    
    def _monitoring_loop(self):
        while self.running:
            try:
                self._check_all_websites()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Get current interval from settings
            current_interval = self.get_check_interval()
            time.sleep(current_interval)
    
    def _check_all_websites(self):
        with app.app_context():
            websites = Website.query.filter_by(is_active=True).all()
            
            for website in websites:
                try:
                    self._check_website(website)
                except Exception as e:
                    logger.error(f"Error checking website {website.url}: {e}")
    
    def _check_website(self, website):
        start_time = time.time()
        
        try:
            # Set a reasonable timeout
            response = requests.get(website.url, timeout=10, allow_redirects=True)
            response_time = time.time() - start_time
            
            # Consider 2xx and 3xx status codes as success
            is_up = 200 <= response.status_code < 400
            
            result = MonitoringResult(
                website_id=website.id,
                is_up=is_up,
                status_code=response.status_code,
                response_time=response_time,
                checked_at=datetime.utcnow()
            )
            
            if is_up:
                logger.info(f"Successfully visited {website.url} - Status: {response.status_code}")
            else:
                result.error_message = f"HTTP {response.status_code}"
                logger.warning(f"Website {website.url} returned status {response.status_code}")
            
        except requests.exceptions.Timeout:
            result = MonitoringResult(
                website_id=website.id,
                is_up=False,
                response_time=time.time() - start_time,
                error_message="Request timeout",
                checked_at=datetime.utcnow()
            )
            logger.warning(f"Timeout checking {website.url}")
            
        except requests.exceptions.ConnectionError:
            result = MonitoringResult(
                website_id=website.id,
                is_up=False,
                response_time=time.time() - start_time,
                error_message="Connection error",
                checked_at=datetime.utcnow()
            )
            logger.warning(f"Connection error checking {website.url}")
            
        except requests.exceptions.RequestException as e:
            result = MonitoringResult(
                website_id=website.id,
                is_up=False,
                response_time=time.time() - start_time,
                error_message=str(e),
                checked_at=datetime.utcnow()
            )
            logger.error(f"Request error checking {website.url}: {e}")
        
        # Save result to database
        db.session.add(result)
        db.session.commit()

# Global monitoring service instance
monitoring_service = MonitoringService()

def start_monitoring_service():
    """Start the background monitoring service"""
    monitoring_service.start()

def stop_monitoring_service():
    """Stop the background monitoring service"""
    monitoring_service.stop()
