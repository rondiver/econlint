# Should trigger ECON004 - asyncio.gather without semaphore
import asyncio

async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)
