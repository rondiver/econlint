# Should NOT trigger ECON002 - has stop parameter
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def fetch_data():
    return requests.get("/data")
