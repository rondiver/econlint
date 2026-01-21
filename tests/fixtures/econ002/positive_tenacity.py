# Should trigger ECON002 - tenacity retry without stop
from tenacity import retry

@retry()
def fetch_data():
    return requests.get("/data")
