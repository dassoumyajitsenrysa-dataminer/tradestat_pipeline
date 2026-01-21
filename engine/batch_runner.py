import asyncio
from pipeline.chunker import chunk_list
from pipeline.scheduler import run_chunks_parallel
from pipeline.worker import process_chunk_with_pool
from utils.hs_code_db import HSCodeDatabase
from scraper.browser_pool import close_global_pool
from utils.logger import get_logger

logger = get_logger("batch_runner")


async def _process_chunk_with_db(chunk, db):
    """Wrapper to pass db to process_chunk"""
    await process_chunk_with_pool(chunk, db=db)


async def run_scheduler(chunks, year, max_parallel, db=None):
    """Run chunks in parallel with database tracking"""
    if db is None:
        db = HSCodeDatabase()
    
    semaphore = asyncio.Semaphore(max_parallel)

    async def sem_task(chunk):
        async with semaphore:
            await _process_chunk_with_db(chunk, db)

    tasks = [sem_task(chunk) for chunk in chunks]
    await asyncio.gather(*tasks)


def start_batch(year: str, chunk_size: int = 25, max_parallel: int = 3):
    """
    Entry point for batch scraping.
    Uses database to track only pending HS codes.
    
    Optimizations:
    - Browser pooling (reuse instances)
    - Exponential backoff on failures
    - Request throttling
    """

    logger.info("=== TRADESTAT BATCH PIPELINE STARTED ===")
    logger.info(f"Using {max_parallel} parallel workers with browser pooling")

    # Get pending HS codes from database
    db = HSCodeDatabase()
    pending_codes = db.get_pending()

    logger.info(f"Loaded {len(pending_codes)} pending HS codes from database")

    if not pending_codes:
        logger.info("Nothing to process. Exiting.")
        stats = db.get_stats()
        logger.info(f"Stats: {stats}")
        return

    chunks = chunk_list(pending_codes, chunk_size)

    logger.info(f"Split into {len(chunks)} chunks of {chunk_size} codes each")

    try:
        asyncio.run(
            run_scheduler(
                chunks=chunks,
                year=year,
                max_parallel=max_parallel,
                db=db
            )
        )
    finally:
        # Cleanup browser pool
        asyncio.run(close_global_pool())
        logger.info("Browser pool closed")

    logger.info("=== BATCH PIPELINE COMPLETED ===")
    stats = db.get_stats()
    logger.info(f"Final Stats: {stats}")
