from scraper.controller import ScraperController
from scraper.browser_pool import get_global_pool, close_global_pool
from storage.json_writer import JSONWriter
from storage.processor import Processor
from storage.normalizer import Normalizer
from utils.retry_manager import retry_async, SCRAPER_RETRY_CONFIG
from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR, NORMALIZED_DATA_DIR
from utils.logger import get_logger
from utils.hs_code_db import HSCodeDatabase
from pathlib import Path
import traceback
import asyncio
from datetime import datetime


print("WORKER FILE LOADED FROM:", __file__)

logger = get_logger("WORKER")


async def _scrape_mode_with_retry(hs, mode):
    """Scrape a single trade mode with automatic retry on failure"""
    try:
        controller = ScraperController(trade_mode=mode, use_pool=True)
        
        # Retry logic: automatically retries 3 times with exponential backoff
        result = await retry_async(
            controller.run,
            hs,
            config=SCRAPER_RETRY_CONFIG,
            retriable_exceptions=(
                Exception,  # Catch all exceptions for now
            )
        )
        
        if result and result.get("status") != "FAILED":
            return mode, result
        return mode, None
    except Exception as e:
        logger.warning(f"Failed to scrape {mode} for {hs} after retries: {str(e)}")
        return mode, None


async def process_chunk(chunk, db: HSCodeDatabase = None):
    """Process a chunk of HS codes"""
    raw_writer = JSONWriter()
    processed_writer = JSONWriter()
    
    if db is None:
        db = HSCodeDatabase()
    
    for hs in chunk:
        try:
            logger.info(f"Processing HS: {hs}")

            start_time = datetime.now()

            # -------- SCRAPE (PARALLEL WITH RETRY) --------
            # Run export and import scraping in parallel with auto-retry
            tasks = [
                _scrape_mode_with_retry(hs, "export"),
                _scrape_mode_with_retry(hs, "import")
            ]
            mode_results = await asyncio.gather(*tasks)
            
            results = {mode: result for mode, result in mode_results if result is not None}
            
            if not results:
                logger.error(f"HS failed {hs} → No successful results from any trade mode")
                db.mark_failed(hs, "Failed to scrape both export and import after retries")
                continue

            # Process each trade mode separately
            for trade_mode in ["export", "import"]:
                if trade_mode not in results:
                    logger.info(f"Skipping {trade_mode} for {hs} - no data")
                    continue
                
                try:
                    result = results[trade_mode]
                    
                    # ---------- SAVE RAW ----------
                    raw_file = raw_writer.write(
                        base_dir=Path(RAW_DATA_DIR),
                        trade_mode=trade_mode,
                        hs_code=hs,
                        payload=result
                    )

                    # ---------- PROCESS ----------
                    processed = Processor.process_raw_payload(result)

                    # ---------- SAVE PROCESSED ----------
                    processed_file = processed_writer.write(
                        base_dir=Path(PROCESSED_DATA_DIR),
                        trade_mode=trade_mode,
                        hs_code=hs,
                        payload=processed
                    )

                    # ---------- NORMALIZE ----------
                    Normalizer.write_normalized_file(
                        processed_file_path=processed_file,
                        normalized_root=Path(NORMALIZED_DATA_DIR)
                    )

                    # Mark as completed in database
                    if trade_mode == "export":
                        db.mark_export_completed(hs)
                    else:
                        db.mark_import_completed(hs)
                    
                    logger.info(f"HS {hs} ({trade_mode}) completed ✓")

                except Exception as mode_err:
                    db.mark_failed(hs, str(mode_err), trade_mode=trade_mode)
                    logger.error(f"HS {hs} ({trade_mode}) failed\n{traceback.format_exc()}")

            # Mark overall completion if both modes done
            if "export" in results and "import" in results:
                db.mark_completed(hs)

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"HS {hs} completed in {elapsed:.2f} sec ✓")

        except Exception:
            db.mark_failed(hs, traceback.format_exc())
            logger.error(f"HS {hs} failed\n{traceback.format_exc()}")


async def process_chunk_with_pool(chunk, db: HSCodeDatabase = None):
    """
    Process chunk with browser pool initialization and cleanup.
    Call this instead of process_chunk directly.
    """
    try:
        # Initialize browser pool before processing
        pool = await get_global_pool(pool_size=4)
        logger.info("Browser pool ready for chunk processing")
        
        # Process the chunk
        await process_chunk(chunk, db)
        
    finally:
        # Note: Don't close pool here - it will be reused by next chunk
        # Close pool only when shutting down entire pipeline
        pass
