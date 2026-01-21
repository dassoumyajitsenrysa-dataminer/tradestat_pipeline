#!/usr/bin/env python
"""
Periodic database sync - updates MongoDB with latest scraped data
Syncs from local MongoDB to MongoDB Atlas automatically

Usage:
    python sync_database.py --interval 3600  # Sync every hour
    python sync_database.py --interval 86400 # Sync daily
"""

import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import get_logger

logger = get_logger("DB_SYNC")

LOCAL_MONGO_URI = "mongodb://localhost:27017"
ATLAS_MONGO_URI = os.getenv("MONGO_URI", "")


def sync_databases():
    """Sync data from local MongoDB to MongoDB Atlas"""
    try:
        logger.info("=" * 60)
        logger.info(f"DATABASE SYNC STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Connect to local MongoDB
        try:
            local_client = MongoClient(LOCAL_MONGO_URI, serverSelectionTimeoutMS=2000)
            local_client.server_info()
            local_db = local_client["tradestat"]
            logger.info("✓ Connected to local MongoDB")
        except Exception as e:
            logger.error(f"✗ Failed to connect to local MongoDB: {str(e)}")
            return False
        
        # Connect to MongoDB Atlas (if configured)
        if not ATLAS_MONGO_URI:
            logger.warning("⚠ MONGO_URI not set - skipping Atlas sync")
            logger.info("  Set MONGO_URI environment variable to sync to Atlas")
            return True
        
        try:
            atlas_client = MongoClient(ATLAS_MONGO_URI, serverSelectionTimeoutMS=2000)
            atlas_client.server_info()
            atlas_db = atlas_client["tradestat"]
            logger.info("✓ Connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"✗ Failed to connect to MongoDB Atlas: {str(e)}")
            return False
        
        # Sync collections
        collections_to_sync = ["hs_codes", "partner_countries"]
        total_synced = 0
        
        for collection_name in collections_to_sync:
            try:
                local_col = local_db[collection_name]
                atlas_col = atlas_db[collection_name]
                
                # Get all documents from local
                docs = list(local_col.find({}))
                
                if docs:
                    # Remove MongoDB IDs for clean insert
                    for doc in docs:
                        doc.pop("_id", None)
                    
                    # Clear Atlas collection and insert all from local
                    atlas_col.delete_many({})
                    result = atlas_col.insert_many(docs)
                    
                    count = len(result.inserted_ids)
                    total_synced += count
                    logger.info(f"  ✓ Synced {count} documents to {collection_name}")
                else:
                    logger.info(f"  ℹ No documents in {collection_name}")
            
            except Exception as e:
                logger.error(f"  ✗ Failed to sync {collection_name}: {str(e)}")
                continue
        
        logger.info(f"\n✓ Total documents synced: {total_synced}")
        logger.info("=" * 60)
        logger.info("DATABASE SYNC COMPLETED")
        logger.info("=" * 60 + "\n")
        
        return True
    
    except Exception as e:
        logger.error(f"Database sync failed: {str(e)}")
        return False


def run_periodic_sync(interval_seconds=3600):
    """Run database sync periodically"""
    logger.info(f"Starting periodic sync (interval: {interval_seconds}s)")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        while True:
            sync_databases()
            
            # Wait for next sync
            logger.info(f"Next sync in {interval_seconds}s...")
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        logger.info("\n\nSync stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync MongoDB data periodically")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Sync interval in seconds (default: 3600 = 1 hour)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run sync once and exit"
    )
    
    args = parser.parse_args()
    
    if args.once:
        # Run once and exit
        sync_databases()
    else:
        # Run periodically
        run_periodic_sync(args.interval)
