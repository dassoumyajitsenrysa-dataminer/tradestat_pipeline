from datetime import datetime, timezone, timedelta
import re
import uuid

IST = timezone(timedelta(hours=5, minutes=30))


class Processor:

    PIPELINE_VERSION = "1.0.0"
    SCHEMA_VERSION = "v1"

    # -------------------------
    # Entry Point
    # -------------------------

    @classmethod
    def process_raw_payload(cls, raw_payload: dict) -> dict:

        # ---- Schema Validation ----
        if "metadata" not in raw_payload or "hs_code" not in raw_payload["metadata"]:
            raise ValueError(f"Invalid raw payload: missing hs_code -> {raw_payload.keys()}")

        if "data_by_year" not in raw_payload:
            raise ValueError(f"Invalid raw payload: missing data_by_year -> {raw_payload.keys()}")

        hs_code = raw_payload["metadata"]["hs_code"]


        # ---- Build Processed Object ----
        processed = {
            "record_id": str(uuid.uuid4()),
            "schema_version": cls.SCHEMA_VERSION,
            "pipeline_version": cls.PIPELINE_VERSION,
            "processed_at_ist": cls.now_ist(),
            
            # Preserve original metadata
            "metadata": raw_payload["metadata"],

            "hs": cls.parse_hs(hs_code),

            "trade_type": "EXPORT",
            "frequency": "ANNUAL",

            "source": {
                "site": "https://tradestat.commerce.gov.in",
                "dataset": "Commodity-wise all Countries",
                "country": "India",
            },

            "years": {}
        }

        # ---- Process Each Year ----
        for year, block in raw_payload["data_by_year"].items():

            processed["years"][year] = {
                "product_label": block.get("product_label"),
                "summary": cls.clean_summary(block.get("summary")),
                "partner_countries": cls.clean_rows(block.get("partner_countries")),
                "total_pages": block.get("total_pages")
            }

        return processed

    # -------------------------
    # HS Parser
    # -------------------------

    @staticmethod
    def parse_hs(hs_code: str):

        return {
            "hs8": hs_code,
            "sub_heading": hs_code[:6],
            "heading": hs_code[:4],
            "chapter": hs_code[:2]
        }

    # -------------------------
    # Summary Cleaner
    # -------------------------

    @staticmethod
    def clean_summary(summary: dict):

        if not summary:
            return None

        def clean(x):
            if x is None:
                return None
            return x.replace(",", "").strip()

        return {
            "total_exports_selected_countries": {
                "prev": clean(summary["total_exports_selected_countries"].get("2023_24")),
                "curr": clean(summary["total_exports_selected_countries"].get("2024_25")),
                "growth": clean(summary["total_exports_selected_countries"].get("growth_percent"))
            },
            "india_total_exports": {
                "prev": clean(summary["india_total_exports"].get("2023_24")),
                "curr": clean(summary["india_total_exports"].get("2024_25")),
                "growth": clean(summary["india_total_exports"].get("growth_percent"))
            },
            "share_of_india_exports_percent": {
                "prev": clean(summary["share_of_india_exports_percent"].get("2023_24")),
                "curr": clean(summary["share_of_india_exports_percent"].get("2024_25")),
                "growth": clean(summary["share_of_india_exports_percent"].get("growth_percent"))
            }
        }

    # -------------------------
    # Row Cleaner
    # -------------------------

    @staticmethod
    def clean_rows(rows):

        cleaned = []

        if not rows:
            return cleaned

        for r in rows:

            obj = {}

            for k, v in r.items():

                if isinstance(v, str):
                    v = v.strip()

                    # numeric normalization
                    if re.match(r"^-?\d+(\.\d+)?$", v.replace(",", "")):
                        v = v.replace(",", "")

                obj[k] = v

            cleaned.append(obj)

        return cleaned

    # -------------------------
    # Utilities
    # -------------------------

    @staticmethod
    def now_ist():
        return datetime.now(IST).isoformat()
