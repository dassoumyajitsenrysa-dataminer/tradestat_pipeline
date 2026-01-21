from utils.logger import get_logger

logger = get_logger("form_handler")


class FormHandler:

    # Selector mappings for different trade modes
    SELECTORS = {
        "export": {
            "hs_code": "#Eidbhscode_cmace",
            "year": "#EidbYear_cmace"
        },
        "import": {
            "hs_code": "#Eidbhscode_cmaci",
            "year": "#EidbYear_cmaci"
        }
    }

    def __init__(self, page, trade_mode: str = "export"):
        self.page = page
        self.trade_mode = trade_mode.lower()
        self.selectors = self.SELECTORS.get(self.trade_mode, self.SELECTORS["export"])
        logger.info(f"FormHandler initialized for trade_mode: {self.trade_mode}")

    async def fill_hs_code(self, hs_code: str):
        logger.info(f"Filling HS code: {hs_code} using selector {self.selectors['hs_code']}")
        await self.page.fill(self.selectors["hs_code"], "")
        await self.page.fill(self.selectors["hs_code"], hs_code)

    # -------------------------------------------------
    # Get ALL available years dynamically
    # -------------------------------------------------
    async def get_all_years(self):
        logger.info(f"Getting years using selector {self.selectors['year']}")
        dropdown = await self.page.wait_for_selector(self.selectors["year"])

        options = await dropdown.query_selector_all("option")

        years = []
        for opt in options:
            txt = (await opt.inner_text()).strip()
            if "-" in txt:
                years.append(txt)

        if not years:
            raise RuntimeError("No year options found")

        logger.info(f"Available years: {years}")

        return years

    # -------------------------------------------------
    # Select a specific year
    # -------------------------------------------------
    async def select_year(self, year_label: str):
        logger.info(f"Selecting year: {year_label} using selector {self.selectors['year']}")
        await self.page.select_option(self.selectors["year"], label=year_label)

    # -------------------------------------------------
    async def submit(self):
        logger.info("Submitting form")
        await self.page.click("button[type=submit]")
        await self.page.wait_for_load_state("networkidle")
