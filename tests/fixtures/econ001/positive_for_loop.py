# Should trigger ECON001 - external call in for loop
import requests

def sync_users(users):
    for user in users:
        response = requests.get(f"https://api.example.com/users/{user.id}")
        user.data = response.json()
