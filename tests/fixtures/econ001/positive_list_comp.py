# Should trigger ECON001 - external call in list comprehension
import httpx

def fetch_all(ids):
    return [httpx.get(f"/items/{id}") for id in ids]
