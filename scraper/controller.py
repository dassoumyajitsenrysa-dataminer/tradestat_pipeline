from scraper.browser import BrowserManager
from scraper.browser_pool import get_global_pool
from scraper.form_handler import FormHandler
from scraper.paginator import Paginator
from scraper.table_parser import TableParser
from scraper.summary_parser import SummaryParser
from utils.logger import get_logger
from utils.request_throttler import get_throttler
from config.settings import BASE_URLS
from datetime import datetime, timezone
import time

logger = get_logger("CONTROLLER")


class ScraperController:

    # Selector mappings for different trade modes
    SELECTORS = {
        "export": "#Eidbhscode_cmace",
        "import": "#Eidbhscode_cmaci"
    }

    def __init__(self, trade_mode: str = "export", use_pool: bool = True):
        """
        trade_mode: export | import
        use_pool: Use browser pooling (True) or create new browser (False)
        """
        self.trade_mode = trade_mode.lower()
        self.use_pool = use_pool

    # -------------------------------------------------
    async def run(self, hs_code: str):
        start_ts = time.time()

        # Use browser from pool if enabled
        if self.use_pool:
            pool = await get_global_pool(pool_size=4)
            page = await pool.get_browser()
        else:
            browser = BrowserManager()
            page = await browser.start()

        try:
            # Get throttler for rate limiting
            throttler = get_throttler(min_delay=1.5, max_delay=3.0)
            
            url = self._build_url()
            logger.info(f"Opening URL: {url}")
            url = self._build_url()
            logger.info(f"Opening URL: {url}")

            await page.goto(url, wait_until="networkidle", timeout=120000)
            logger.info("Page loaded, waiting for form element...")
            
            selector = self.SELECTORS.get(self.trade_mode, self.SELECTORS["export"])
            logger.info(f"Waiting for selector: {selector}")
            await page.wait_for_selector(selector, timeout=120000)

            # ---------------- FORM ----------------
            form = FormHandler(page, trade_mode=self.trade_mode)
            await form.fill_hs_code(hs_code)

            years = await form.get_all_years()
            logger.info(f"Available years: {years}")

            all_year_data = {}

            for year in years:
                logger.info(f"Processing {hs_code} for year {year}")

                await form.select_year(year)
                await form.submit()

                # Wait table to load
                await page.wait_for_selector("#example1 tbody tr", timeout=60000)

                # ---------------- PRODUCT LABEL ----------------
                product_label = None
                try:
                    label = await page.locator("xpath=//*[contains(text(),'Commodity:')]").first.inner_text()
                    product_label = label.replace("Commodity:", "").strip()
                except:
                    logger.warning("Product label not found")

                # ---------------- TABLE ----------------
                table_parser = TableParser(page)
                paginator = Paginator(page, table_parser)
                rows, total_pages = await paginator.scrape_all_pages()

                # ---------------- SUMMARY ----------------
                summary = None
                try:
                    await page.wait_for_selector("#example1 tfoot tr", timeout=30000)
                    summary_parser = SummaryParser(page)
                    summary = await summary_parser.parse()
                except:
                    logger.warning("Summary not available")

                partner_countries = self.map_rows(rows, year)

                all_year_data[year] = {
                    "product_label": product_label,
                    "partner_countries": partner_countries,
                    "summary": summary,
                    "total_pages": total_pages
                }

            # ---------------- METADATA ----------------
            end_ts = time.time()
            
            # Count data completeness
            total_records = 0
            complete_records = 0
            for year_data in all_year_data.values():
                partners = year_data.get("partner_countries", [])
                total_records += len(partners)
                complete_records += len([p for p in partners if p.get("Country")])

            metadata = {
                "hs_code": hs_code,
                "trade_mode": self.trade_mode,
                "report_type": "Commodity wise all Countries",
                "data_frequency": "Annual",
                "currency": "USD Million",
                "quantity_unit": "As reported by site",
                "source_site": url,
                
                # Timestamps
                "scraped_at_ist": self._ist_now(),
                "scrape_duration_seconds": round(end_ts - start_ts, 2),
                
                # Data Quality
                "total_records_captured": total_records,
                "complete_records": complete_records,
                "data_completeness_percent": round((complete_records / total_records * 100), 2) if total_records > 0 else 0,
                "years_available": list(all_year_data.keys()),
                "number_of_years": len(all_year_data),
                
                # Count unique partner countries
                "unique_partner_countries": len(set(
                    p.get("Country", "Unknown") 
                    for year_data in all_year_data.values() 
                    for p in year_data.get("partner_countries", [])
                )),
                
                # Performance
                "page_load_time_ms": round((end_ts - start_ts) * 1000, 2),
                
                # Versioning
                "pipeline_version": "v1",
                "controller_version": "1.0.0",
                "scraper_environment": "production",
                
                # HS Code Hierarchy
                "hs_hierarchy": self.parse_hs(hs_code),
                
                # Data Source Info
                "data_currency_unit": "USD Million",
                "data_availability_note": "2017-2018 to 2025-2026",
            }

            return {
                "status": "SUCCESS",
                "metadata": metadata,
                "data_by_year": all_year_data
            }

        finally:
            # Return browser to pool or close it
            if self.use_pool:
                pool = await get_global_pool()
                await pool.return_browser(page)
            else:
                await page.close()

    # -------------------------------------------------
    def _build_url(self):
        if self.trade_mode == "export":
            return BASE_URLS["export"]
        elif self.trade_mode == "import":
            return BASE_URLS["import"]
        else:
            raise ValueError("Invalid trade_mode. Use 'export' or 'import'")

    # -------------------------------------------------
    @staticmethod
    def parse_hs(hs):
        return {
            "chapter": hs[:2],
            "heading": hs[:4],
            "sub_heading": hs[:6],
            "hs_8": hs
        }

    # -------------------------------------------------
    @staticmethod
    def _ist_now():
        return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S IST")

    # -------------------------------------------------
    @staticmethod
    def build_headers(year: str):
        y1, y2 = year.split("-")
        prev = f"{int(y1)-1}-{y1}"
        curr = year

        return [
            "S.No",
            "Country",
            prev,
            curr,
            "%Growth",
            f"Qty_{prev.replace('-', '_')}",
            f"Qty_{curr.replace('-', '_')}",
            "Qty_Growth"
        ]

    # -------------------------------------------------
    @classmethod
    def map_rows(cls, rows, year):
        headers = cls.build_headers(year)
        mapped = []

        for r in rows:
            mapped.append({
                headers[i]: r[i].strip() if i < len(r) and r[i] else None
                for i in range(len(headers))
            })

        return mapped
