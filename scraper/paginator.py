from utils.logger import get_logger

logger = get_logger("paginator")

class Paginator:

    def __init__(self, page, table_parser):
        self.page = page
        self.table_parser = table_parser

    async def scrape_all_pages(self):
        all_records = []
        page_count = 0

        while True:
            page_count += 1
            logger.info(f"Scraping page {page_count}")

            records = await self.table_parser.parse_current_page()
            all_records.extend(records)

            next_btn = await self.page.query_selector("li.page-item.next:not(.disabled)")
            if not next_btn:
                break

            await next_btn.click()
            await self.page.wait_for_timeout(1000)

        return all_records, page_count
