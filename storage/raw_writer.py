import json
from config.settings import RAW_DATA_DIR

def save_raw_json(hs_code, data):
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    path = RAW_DATA_DIR / f"{hs_code}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
