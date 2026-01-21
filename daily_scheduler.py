"""
Daily scheduler for trade data scraping.
Runs at a specified time each day and scrapes only new HS codes.

Setup:
    pip install schedule APScheduler
    
Run:
    python scheduler.py --time 02:00  # Run at 2 AM daily
    or
    python scheduler.py --time 14:30  # Run at 2:30 PM daily
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from engine.batch_runner import start_batch
from utils.logger import get_logger

logger = get_logger("SCHEDULER")


def run_daily_scrape():
    """Entry point for scheduled scraping"""
    try:
        logger.info("=" * 60)
        logger.info("SCHEDULED SCRAPE STARTED")
        logger.info("=" * 60)
        
        # Get current year-month for tracking
        now = datetime.now()
        year = f"{now.year}-{now.month:02d}"
        
        # Run batch scraper with configured parameters
        start_batch(
            year=year,
            chunk_size=50,          # HS codes per chunk
            max_parallel=4          # Parallel workers
        )
        
        logger.info("=" * 60)
        logger.info("SCHEDULED SCRAPE COMPLETED")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Scheduled scrape failed: {str(e)}\n{traceback.format_exc()}")


def setup_scheduler(hour: int, minute: int):
    """
    Setup background scheduler to run daily at specified time.
    
    Args:
        hour: 0-23 (24-hour format)
        minute: 0-59
    """
    scheduler = BackgroundScheduler()
    
    # Add daily job at specified time
    scheduler.add_job(
        run_daily_scrape,
        'cron',
        hour=hour,
        minute=minute,
        id='daily_scrape'
    )
    
    scheduler.start()
    
    logger.info(f"Scheduler started. Running daily at {hour:02d}:{minute:02d}")
    logger.info("Press Ctrl+C to stop the scheduler")
    
    try:
        # Keep scheduler running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    import traceback
    
    parser = argparse.ArgumentParser(description="Daily trade scraper scheduler")
    parser.add_argument(
        "--time",
        type=str,
        default="02:00",
        help="Time to run daily (HH:MM format, e.g., 02:00, 14:30)"
    )
    
    args = parser.parse_args()
    
    # Parse time
    time_parts = args.time.split(":")
    if len(time_parts) != 2:
        print("Error: Time format must be HH:MM (e.g., 02:00)")
        exit(1)
    
    try:
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time values")
        
        setup_scheduler(hour, minute)
    except (ValueError, TypeError) as e:
        print(f"Error parsing time: {e}")
        print("Time format must be HH:MM (e.g., 02:00, 14:30)")
        exit(1)
