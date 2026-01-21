import asyncio
from pipeline.worker import process_chunk


async def run_chunks_parallel(chunks, max_workers):
    semaphore = asyncio.Semaphore(max_workers)

    async def sem_task(chunk):
        async with semaphore:
            await process_chunk(chunk)

    tasks = [sem_task(chunk) for chunk in chunks]
    await asyncio.gather(*tasks)
