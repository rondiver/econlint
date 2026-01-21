# Should NOT report - suppressed
def load_user_details(user_ids, api):
    for user_id in user_ids:
        details = api.get_user(user_id)  # econlint: ignore
        print(details)
