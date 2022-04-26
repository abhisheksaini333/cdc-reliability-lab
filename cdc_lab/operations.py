
from . import runtime

def select_job(overview):
    jobs = [job for job in overview.get("jobs", []) if job.get("state") == "RUNNING"]
    if len(jobs) != 1:
        raise RuntimeError("expected exactly one running pipeline; inspect Flink jobs")
    return jobs[0]["jid"]

def active_job():
    return select_job(runtime.http_json("http://127.0.0.1:4704/jobs/overview"))
