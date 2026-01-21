# Should NOT trigger ECON001 - batched call outside loop
import requests

def sync_users(user_ids):
    # Batch call outside loop
    response = requests.post("https://api.example.com/users/batch", json=user_ids)
    users_data = response.json()

    for user_id, data in zip(user_ids, users_data):
        print(f"User {user_id}: {data}")
