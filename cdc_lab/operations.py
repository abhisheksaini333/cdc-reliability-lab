
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

def savepoint_result(status):
    if status.get("status", {}).get("id") != "COMPLETED":
        return None
    operation = status.get("operation", {})
    if "failure-cause" in operation or not operation.get("location"):
        raise RuntimeError("Flink savepoint failed")
    return operation["location"]

def savepoint(cancel=False):
    job = active_job()
    base = "http://127.0.0.1:4704/jobs/" + job + "/savepoints"
    request = runtime.http_json(base, {"target-directory": "file:///state/savepoints", "cancel-job": cancel}, "POST")
    return runtime.wait_for(lambda: savepoint_result(runtime.http_json(base + "/" + request["request-id"])), timeout=120)

def restart_service_name(name):
    if name not in ("taskmanager", "connect", "kafka", "clickhouse"):
        raise ValueError("restart target is outside lab recovery scenarios")
    return name

def restart(name):
    runtime.compose("restart", restart_service_name(name), timeout=120)
