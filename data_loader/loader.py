"""
Data loader to migrate all scraped JSON files into MongoDB.
Handles JSON loading, validation with Pydantic models, and bulk inserts.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import MongoDatabase
from api.models import HSCodeRecord
from utils.logger import get_logger

logger = get_logger("DATA_LOADER")


class DataLoader:
    """Load JSON data from files into MongoDB"""
    
    def __init__(self):
        self.db = MongoDatabase.get_instance()
        self.collection = self.db.get_collection("hs_codes")
        self.stats = {
            "loaded": 0,
            "updated": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
    
    def load_from_directory(self, directory: Path, pattern: str = "*.json") -> None:
        """Load all JSON files from a directory"""
        json_files = sorted(directory.rglob(pattern))
        total_files = len(json_files)
        
        logger.info(f"Found {total_files} JSON files in {directory}")
        
        for idx, json_file in enumerate(json_files, 1):
            self._load_file(json_file, idx, total_files)
    
    def _load_file(self, json_file: Path, current: int, total: int) -> None:
        """Load a single JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both single record and list of records
            if isinstance(data, list):
                records = data
            else:
                records = [data]
            
            for record in records:
                self._insert_record(record)
            
            # Log progress
            if current % 10 == 0 or current == total:
                logger.info(
                    f"Progress: {current}/{total} | "
                    f"Loaded: {self.stats['loaded']}, "
                    f"Updated: {self.stats['updated']}, "
                    f"Failed: {self.stats['failed']}"
                )
        
        except json.JSONDecodeError as e:
            self.stats['failed'] += 1
            error_msg = f"JSON decode error in {json_file.name}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        except Exception as e:
            self.stats['failed'] += 1
            error_msg = f"Error loading {json_file.name}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
    
    def _insert_record(self, record: Dict[str, Any]) -> None:
        """Insert or update a single record"""
        try:
            # Validate with Pydantic model
            validated_record = HSCodeRecord(**record)
            record_dict = validated_record.dict()
            
            # Use upsert to handle duplicates
            # Key is combination of hs_code and trade_mode
            hs_code = record_dict.get("hs_code")
            trade_mode = record_dict.get("trade_mode")
            
            if not hs_code or not trade_mode:
                self.stats['skipped'] += 1
                return
            
            # Check if record exists
            existing = self.collection.find_one({
                "hs_code": hs_code,
                "trade_mode": trade_mode
            })
            
            if existing:
                # Update with new data
                self.collection.update_one(
                    {"hs_code": hs_code, "trade_mode": trade_mode},
                    {"$set": record_dict},
                    upsert=True
                )
                self.stats['updated'] += 1
            else:
                # Insert new record
                self.collection.insert_one(record_dict)
                self.stats['loaded'] += 1
        
        except Exception as e:
            self.stats['failed'] += 1
            error_msg = f"Failed to validate/insert record {record.get('hs_code')}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
    
    def print_summary(self) -> None:
        """Print loading summary"""
        logger.info("=" * 60)
        logger.info("DATA LOADING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Loaded:    {self.stats['loaded']}")
        logger.info(f"Total Updated:   {self.stats['updated']}")
        logger.info(f"Total Failed:    {self.stats['failed']}")
        logger.info(f"Total Skipped:   {self.stats['skipped']}")
        logger.info(f"Total Records:   {self.stats['loaded'] + self.stats['updated']}")
        
        if self.stats['errors']:
            logger.info("\nERRORS ENCOUNTERED:")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                logger.error(f"  - {error}")
            if len(self.stats['errors']) > 10:
                logger.info(f"  ... and {len(self.stats['errors']) - 10} more errors")
        
        logger.info("=" * 60)
        
        return self.stats


def load_all_data():
    """Load all processed and raw data into MongoDB"""
    
    base_path = Path(__file__).parent.parent / "data"
    
    loader = DataLoader()
    
    # Load processed data (priority)
    processed_path = base_path / "processed"
    if processed_path.exists():
        logger.info(f"\nLoading PROCESSED data from {processed_path}")
        logger.info("-" * 60)
        loader.load_from_directory(processed_path)
    else:
        logger.warning(f"Processed directory not found: {processed_path}")
    
    # Load raw data (fallback)
    raw_path = base_path / "raw"
    if raw_path.exists():
        logger.info(f"\nLoading RAW data from {raw_path}")
        logger.info("-" * 60)
        loader.load_from_directory(raw_path)
    else:
        logger.warning(f"Raw directory not found: {raw_path}")
    
    # Print summary
    stats = loader.print_summary()
    
    # Verify data in database
    total_in_db = loader.collection.count_documents({})
    export_count = loader.collection.count_documents({"trade_mode": "export"})
    import_count = loader.collection.count_documents({"trade_mode": "import"})
    
    logger.info("\nDATABASE VERIFICATION:")
    logger.info(f"Total records in MongoDB: {total_in_db}")
    logger.info(f"  Export records: {export_count}")
    logger.info(f"  Import records: {import_count}")
    
    return stats


if __name__ == "__main__":
    logger.info("Starting data migration to MongoDB...")
    logger.info("=" * 60)
    
    load_all_data()
    
    logger.info("\nData loading complete!")
