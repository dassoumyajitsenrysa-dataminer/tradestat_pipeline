from playwright.async_api import async_playwright
from utils.logger import get_logger

logger = get_logger("browser")


class BrowserManager:

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None

    async def start(self):
        logger.info("Starting Playwright browser")

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800}
        )

        page = await context.new_page()

        logger.info("Browser ready")

        return page

    async def close(self):
        logger.info("Closing browser")

        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Browser close issue: {e}")
