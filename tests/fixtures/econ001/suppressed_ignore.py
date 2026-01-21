# Should NOT report - suppressed with ignore comment
import requests

def sync_users(users):
    for user in users:
        response = requests.get(f"/users/{user.id}")  # econlint: ignore
        user.data = response.json()
