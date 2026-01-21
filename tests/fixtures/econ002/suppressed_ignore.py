# Should NOT report - suppressed
from tenacity import retry

@retry()  # econlint: ignore=ECON002
def fetch_data():
    return requests.get("/data")
