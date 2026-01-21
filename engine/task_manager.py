import asyncio
from engine.worker import Worker

async def run_workers(chunks, year, max_workers):

    tasks = []

    for i, chunk in enumerate(chunks):
        worker = Worker(i+1)
        tasks.append(worker.run(chunk, year))

        if len(tasks) == max_workers:
            await asyncio.gather(*tasks)
            tasks = []

    if tasks:
        await asyncio.gather(*tasks)
