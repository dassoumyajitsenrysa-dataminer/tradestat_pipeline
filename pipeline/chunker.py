from math import ceil
from utils.logger import get_logger

logger = get_logger("chunker")


def chunk_list(data: list, chunk_size: int) -> list[list]:
    """
    Split a list into chunks of fixed size.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")

    total = len(data)
    total_chunks = ceil(total / chunk_size)

    logger.info(f"Splitting {total} items into {total_chunks} chunks of size {chunk_size}")

    chunks = []

    for i in range(0, total, chunk_size):
        chunks.append(data[i:i + chunk_size])

    return chunks
