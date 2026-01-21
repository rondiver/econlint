# Should trigger ECON002 - while True retry without counter
import time

def fetch_with_retry():
    while True:
        try:
            return do_request()
        except Exception:
            time.sleep(1)
