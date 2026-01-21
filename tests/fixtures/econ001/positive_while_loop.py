# Should trigger ECON001 - external call in while loop

def poll_status(client, job_id):
    while True:
        status = client.get_status(job_id)
        if status == "done":
            break
