# Should NOT trigger ECON003 - uses batch fetch
def load_user_details(user_ids, api):
    all_users = api.get_users_batch(user_ids)
    for user in all_users:
        print(user)
