# Should trigger ECON001 - external call in while loop

def poll_status(api_client, job_id):
    while True:
        status = api_client.get_status(job_id)
        if status == "done":
            break
