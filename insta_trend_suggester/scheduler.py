from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from db import get_database
from instagram_scraper import get_instagram_scraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = get_database()
        self.scraper = get_instagram_scraper()
        
    def fetch_and_store_trends(self):
        """Fetch trending data and store in database"""
        try:
            logger.info("Checking if trends need to be fetched...")
            
            # Check if we need to fetch trends (last fetch > 1 hour ago)
            if not self.db.should_fetch_trends():
                logger.info("Trends are still fresh, skipping fetch")
                return
            
            logger.info("Fetching new trending data...")
            
            # Get trending hashtags (using mock data for now)
            trends = self.scraper.get_trending_hashtags_mock()
            
            if trends:
                # Store in database
                self.db.insert_trending_data(trends)
                logger.info(f"Successfully stored {len(trends)} trending items")
            else:
                logger.warning("No trending data retrieved")
                
        except Exception as e:
            logger.error(f"Error in fetch_and_store_trends: {e}")
    
    def start(self):
        """Start the scheduler"""
        try:
            # Add job to run every 30 minutes
            self.scheduler.add_job(
                func=self.fetch_and_store_trends,
                trigger=IntervalTrigger(minutes=30),
                id='fetch_trends',
                name='Fetch trending Instagram data',
                replace_existing=True
            )
            
            # Run once immediately to populate data
            self.fetch_and_store_trends()
            
            # Start the scheduler
            self.scheduler.start()
            logger.info("Trend scheduler started successfully")
            
            # Shut down the scheduler when exiting the app
            atexit.register(lambda: self.scheduler.shutdown())
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Trend scheduler stopped")

# Global scheduler instance
trend_scheduler = None

def get_trend_scheduler() -> TrendScheduler:
    """Get trend scheduler instance"""
    global trend_scheduler
    if trend_scheduler is None:
        trend_scheduler = TrendScheduler()
    return trend_scheduler

def start_scheduler():
    """Start the trend scheduler"""
    scheduler = get_trend_scheduler()
    scheduler.start()

def stop_scheduler():
    """Stop the trend scheduler"""
    global trend_scheduler
    if trend_scheduler:
        trend_scheduler.stop()
