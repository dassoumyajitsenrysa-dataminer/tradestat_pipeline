from config.settings import INDEX_DIR
from utils.logger import logger

INDEX_FILE = INDEX_DIR / "completed.txt"

INDEX_DIR.mkdir(parents=True, exist_ok=True)

def load_completed():
    if not INDEX_FILE.exists():
        return set()

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def mark_completed(hs_code):
    with open(INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(hs_code + "\n")

    logger.info(f"Marked completed: {hs_code}")
