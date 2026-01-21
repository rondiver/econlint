# Should trigger ECON003 - N+1 pattern with get()
def load_user_details(user_ids, api):
    for user_id in user_ids:
        details = api.get_user(user_id)
        print(details)
