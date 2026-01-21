from pathlib import Path
import json
from datetime import datetime

class Normalizer:

    VERSION = "1.0.0"

    @classmethod
    def normalize_processed_payload(cls, processed: dict):

        normalized_rows = []

        metadata = processed.get("metadata", {})
        hs = processed.get("hs", {})
        data_by_year = processed.get("data_by_year", {})

        for year, year_block in data_by_year.items():

            partner_rows = year_block.get("partner_countries", [])
            summary = year_block.get("summary", {})

            for row in partner_rows:

                flat = {
                    # ---- META ----
                    "pipeline_version": metadata.get("pipeline_version"),
                    "scrape_date_ist": metadata.get("scrape_date_ist"),
                    "scrape_time_ist": metadata.get("scrape_time_ist"),
                    "scrape_duration_sec": metadata.get("scrape_duration_sec"),
                    "site_url": metadata.get("site_url"),
                    "trade_type": metadata.get("trade_type"),
                    "data_frequency": metadata.get("data_frequency"),
                    "currency": metadata.get("currency"),

                    # ---- HS ----
                    "hs_code": hs.get("hs_code"),
                    "chapter": hs.get("chapter"),
                    "heading": hs.get("heading"),
                    "sub_heading": hs.get("sub_heading"),
                    "hs_8": hs.get("hs_8"),

                    # ---- YEAR ----
                    "year": year,

                    # ---- COUNTRY ROW ----
                    **row,

                    # ---- SUMMARY ----
                    "summary_total_selected_prev": summary.get("total_exports_selected_countries", {}).get("prev"),
                    "summary_total_selected_curr": summary.get("total_exports_selected_countries", {}).get("curr"),
                    "summary_total_selected_growth": summary.get("total_exports_selected_countries", {}).get("growth"),

                    "summary_india_prev": summary.get("india_total_exports", {}).get("prev"),
                    "summary_india_curr": summary.get("india_total_exports", {}).get("curr"),
                    "summary_india_growth": summary.get("india_total_exports", {}).get("growth"),

                    "summary_share_prev": summary.get("share_of_india_exports_percent", {}).get("prev"),
                    "summary_share_curr": summary.get("share_of_india_exports_percent", {}).get("curr"),
                }

                normalized_rows.append(flat)

        return normalized_rows


    @classmethod
    def write_normalized_file(cls, processed_file_path, normalized_root):

        processed_file_path = Path(processed_file_path)
        normalized_root = Path(normalized_root)

        with open(processed_file_path, "r", encoding="utf-8") as f:
            processed = json.load(f)

        normalized_rows = cls.normalize_processed_payload(processed)

        date_folder = processed_file_path.parent.name
        hs_code = processed_file_path.stem

        out_dir = normalized_root / date_folder
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / f"{hs_code}_normalized.json"

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(normalized_rows, f, indent=2, ensure_ascii=False)

        return out_file