import asyncio
import time

from pipeline.hs_loader import HSLoader
from pipeline.chunker import Chunker

from scraper.browser import BrowserManager
from scraper.form_handler import FormHandler
from scraper.table_parser import TableParser
from scraper.paginator import Paginator
from scraper.summary_parser import SummaryParser

from storage.json_writer import JSONWriter
from utils.logger import get_logger

logger = get_logger("pipeline_main")


# -------------------------------
# CONFIG
# -------------------------------
HS_FILE = "input/hs_codes.txt"
CHUNK_SIZE = 20          # how many HS codes per browser
MAX_PARALLEL_CHUNKS = 3  # how many browsers run in parallel


# -------------------------------
# SINGLE HS SCRAPE
# -------------------------------
async def scrape_single_hs(page, hs_code, year, writer):
    try:
        logger.info(f"Scraping HS {hs_code}")

        form = FormHandler(page)
        await form.fill_hs_code(hs_code)
        await form.select_year(year)
        await form.submit()

        table_parser = TableParser(page)
        paginator = Paginator(page, table_parser)

        records, total_pages = await paginator.scrape_all_pages()

        summary_parser = SummaryParser(page)
        summary = await summary_parser.parse_summary()

        result = {
            "hs_code": hs_code,
            "year": year,
            "total_pages": total_pages,
            "records": records,
            "summary": summary
        }

        writer.write(hs_code, result)

        logger.info(f"Completed HS {hs_code}")

    except Exception as e:
        logger.error(f"FAILED HS {hs_code} → {repr(e)}")


# -------------------------------
# CHUNK WORKER
# -------------------------------
async def run_chunk(chunk, year):
    logger.info(f"Starting chunk with {len(chunk)} HS codes")

    browser = BrowserManager()
    writer = JSONWriter()

    page = await browser.start()

    await page.goto(
        "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export",
        timeout=60000
    )

    for hs_code in chunk:
        await scrape_single_hs(page, hs_code, year, writer)

    await browser.close()

    logger.info("Chunk completed")


# -------------------------------
# PIPELINE CONTROLLER
# -------------------------------
async def run_pipeline(year: str):
    start_time = time.time()

    hs_codes = HSLoader.load(HS_FILE)
    logger.info(f"Loaded {len(hs_codes)} HS codes")

    chunks = Chunker.chunk(hs_codes, CHUNK_SIZE)
    logger.info(f"Total chunks: {len(chunks)}")

    sem = asyncio.Semaphore(MAX_PARALLEL_CHUNKS)

    async def guarded_chunk(chunk):
        async with sem:
            await run_chunk(chunk, year)

    tasks = [guarded_chunk(chunk) for chunk in chunks]

    await asyncio.gather(*tasks)

    runtime = time.time() - start_time
    logger.info(f"PIPELINE FINISHED in {round(runtime,2)} seconds")


# -------------------------------
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    asyncio.run(run_pipeline(year="2024-2025"))
