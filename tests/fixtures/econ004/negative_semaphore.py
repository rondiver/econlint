# Should NOT trigger ECON004 - uses semaphore
import asyncio

semaphore = asyncio.Semaphore(10)

async def fetch_all(urls):
    tasks = [fetch_with_limit(url) for url in urls]
    return await asyncio.gather(*tasks)

async def fetch_with_limit(url):
    async with semaphore:
        return await fetch(url)
