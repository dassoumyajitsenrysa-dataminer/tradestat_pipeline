from pathlib import Path
import json
from datetime import datetime

class JSONWriter:
    def write(self, base_dir: Path, trade_mode: str, hs_code: str, payload: dict):
        # Extract date from scraped_at_ist timestamp (format: YYYY-MM-DD HH:MM:SS IST)
        scraped_at = payload["metadata"]["scraped_at_ist"]
        date = scraped_at.split()[0]  # Extract YYYY-MM-DD part

        path = (
            base_dir
            / trade_mode
            / date
            / f"HS_{hs_code}.json"
        )

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return path
