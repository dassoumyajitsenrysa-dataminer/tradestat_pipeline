from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FAILED_DIR = DATA_DIR / "failed"
LOG_DIR = DATA_DIR / "logs"
INDEX_DIR = DATA_DIR / "index"
NORMALIZED_DATA_DIR = BASE_DIR / "data" / "normalized"
INPUT_DIR = BASE_DIR / "input"

# Input file
HS_CODE_FILE = INPUT_DIR / "hs_codes.txt"

# Website

BASE_URLS = {
    "export": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_export",
    "import": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_import",
    #"total": "https://tradestat.commerce.gov.in/eidb/commodity_wise_all_countries_total"
}


# Scraping settings
HEADLESS = True
BROWSER_TIMEOUT = 60000

# Pipeline settings
CHUNK_SIZE = 20
MAX_WORKERS = 4
RETRY_LIMIT = 3
