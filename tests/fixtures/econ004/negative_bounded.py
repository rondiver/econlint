# Should NOT trigger ECON004 - has max_workers
from concurrent.futures import ThreadPoolExecutor

def process_items(items):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process, items)
    return list(results)
