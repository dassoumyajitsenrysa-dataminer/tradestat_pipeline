from utils.logger import get_logger

logger = get_logger("table_parser")


class TableParser:

    def __init__(self, page):
        self.page = page

    async def parse_table(self):
        logger.info("Parsing table")

        await self.page.wait_for_selector("table#example1", timeout=60000)

        headers = await self._extract_headers()
        rows = await self._extract_rows(headers)

        logger.info(f"Parsed {len(rows)} rows")
        return rows

    async def _extract_headers(self):
        headers = []

        ths = await self.page.query_selector_all("table#example1 thead tr:last-child th")

        for th in ths:
            txt = (await th.inner_text()).strip()
            headers.append(txt)

        # prepend fixed columns
        headers = ["S.No", "Country"] + headers

        logger.debug(f"Headers: {headers}")
        return headers

    async def _extract_rows(self, headers):
        records = []

        trs = await self.page.query_selector_all("table#example1 tbody tr")

        for tr in trs:
            tds = await tr.query_selector_all("td")

            values = []
            for td in tds:
                txt = (await td.inner_text()).strip()
                values.append(txt)

            # Map safely
            row = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    row[header] = values[i]
                else:
                    row[header] = None

            records.append(row)

        return records
    async def parse_current_page(self):
        rows = await self.page.query_selector_all("#example1 tbody tr")
        records = []

        for row in rows:
            cells = await row.query_selector_all("td")
            values = [ (await c.inner_text()).strip() for c in cells ]
            records.append(values)

        logger.info(f"Parsed {len(records)} rows from page")
        return records
