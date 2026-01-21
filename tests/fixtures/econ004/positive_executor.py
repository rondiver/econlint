# Should trigger ECON004 - ThreadPoolExecutor without max_workers
from concurrent.futures import ThreadPoolExecutor

def process_items(items):
    with ThreadPoolExecutor() as executor:
        results = executor.map(process, items)
    return list(results)
