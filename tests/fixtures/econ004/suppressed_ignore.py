# Should NOT report - suppressed
from concurrent.futures import ThreadPoolExecutor

def process_items(items):
    with ThreadPoolExecutor() as executor:  # econlint: ignore=ECON004
        results = executor.map(process, items)
    return list(results)
