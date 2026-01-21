class SummaryParser:

    def __init__(self, page):
        self.page = page

    async def parse(self):
        # ---- Get year headers dynamically ----
        year_headers = await self.page.query_selector_all(
            "#example1 thead tr:nth-child(2) th"
        )

        years = []
        for h in year_headers:
            txt = (await h.inner_text()).strip()
            if "-" in txt:
                years.append(txt.replace(" ", ""))

        if len(years) < 2:
            return None

        y1, y2 = years[0], years[1]

        # ---- Read summary rows ----
        rows = await self.page.query_selector_all("#example1 tfoot tr")

        if not rows or len(rows) < 3:
            return None

        async def extract(row):
            cells = await row.query_selector_all("td")
            return [ (await c.inner_text()).strip() for c in cells ]

        total = await extract(rows[0])
        india = await extract(rows[1])
        share = await extract(rows[2])

        return {
            "total_exports_selected_countries": {
                y1.replace("-", "_"): total[1] if len(total) > 2 else None,
                y2.replace("-", "_"): total[2] if len(total) > 3 else None,
                "growth_percent": total[3] if len(total) > 4 else None,
            },
            "india_total_exports": {
                y1.replace("-", "_"): india[1] if len(india) > 2 else None,
                y2.replace("-", "_"): india[2] if len(india) > 3 else None,
                "growth_percent": india[3] if len(india) > 4 else None,
            },
            "share_of_india_exports_percent": {
                y1.replace("-", "_"): share[1] if len(share) > 2 else None,
                y2.replace("-", "_"): share[2] if len(share) > 3 else None,
                "growth_percent": None,
            }
        }
