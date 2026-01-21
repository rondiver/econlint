# Should trigger ECON003 - N+1 in list comprehension
def fetch_all_profiles(user_ids, client):
    return [client.fetch_profile(uid) for uid in user_ids]
