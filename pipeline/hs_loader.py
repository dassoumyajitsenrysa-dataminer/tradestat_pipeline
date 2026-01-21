from utils.logger import get_logger

logger = get_logger("hs_loader")


def load_hs_codes(filepath: str) -> list[str]:
    """
    Load HS codes from a text file.
    Each line should contain an 8 digit HS code.
    """

    hs_codes = []
    seen = set()

    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            code = line.strip()

            if not code:
                continue

            if not code.isdigit():
                logger.warning(f"Line {line_no}: Non-numeric HS code skipped: {code}")
                continue

            if len(code) != 8:
                logger.warning(f"Line {line_no}: Invalid length HS code skipped: {code}")
                continue

            if code in seen:
                continue

            seen.add(code)
            hs_codes.append(code)

    logger.info(f"Loaded {len(hs_codes)} valid HS codes")
    return hs_codes
