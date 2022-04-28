
from . import runtime

def select_job(overview):
    jobs = [job for job in overview.get("jobs", []) if job.get("state") == "RUNNING"]
    if len(jobs) != 1:
        raise RuntimeError("expected exactly one running pipeline; inspect Flink jobs")
    return jobs[0]["jid"]

def active_job():
    return select_job(runtime.http_json("http://127.0.0.1:4704/jobs/overview"))

def checkpoint_complete(status):
    return status.get("counts", {}).get("completed", 0) > 0

def checkpoint_status(job=None):
    job = job or active_job()
    return runtime.http_json("http://127.0.0.1:4704/jobs/" + job + "/checkpoints")

def wait_checkpoint(job=None):
    job = job or active_job()
    return runtime.wait_for(lambda: checkpoint_complete(checkpoint_status(job)), timeout=120)
