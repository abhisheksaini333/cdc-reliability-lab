
from . import runtime

def job_id(value):
    import re
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{32}", value):
        raise RuntimeError("invalid Flink job identity")
    return value

def select_job(overview):
    if not isinstance(overview, dict) or not isinstance(overview.get("jobs"), list) or any(not isinstance(job, dict) for job in overview["jobs"]):
        raise RuntimeError("invalid Flink job overview")
    jobs = [job for job in overview.get("jobs", []) if job.get("state") == "RUNNING"]
    if len(jobs) != 1:
        raise RuntimeError("expected exactly one running pipeline; inspect Flink jobs")
    return job_id(jobs[0].get("jid"))

def active_job():
    return select_job(runtime.http_json("http://127.0.0.1:4704/jobs/overview"))

def checkpoint_complete(status):
    if not isinstance(status, dict) or not isinstance(status.get("counts"), dict):
        raise ValueError("invalid checkpoint response")
    count = status["counts"].get("completed", 0)
    if type(count) is not int or count < 0:
        raise ValueError("invalid completed checkpoint count")
    return count > 0

def checkpoint_status(job=None):
    job = job_id(job) if job is not None else active_job()
    return runtime.http_json("http://127.0.0.1:4704/jobs/" + job + "/checkpoints")

def wait_checkpoint(job=None):
    job = job_id(job) if job is not None else active_job()
    return runtime.wait_for(lambda: checkpoint_complete(checkpoint_status(job)), timeout=120)

def savepoint_result(status):
    if not isinstance(status, dict) or not isinstance(status.get("status"), dict) or status["status"].get("id") not in ("IN_PROGRESS", "COMPLETED"):
        raise RuntimeError("invalid Flink savepoint response")
    if status["status"]["id"] == "IN_PROGRESS":
        return None
    operation = status.get("operation", {})
    location = operation.get("location") if isinstance(operation, dict) else None
    if not isinstance(operation, dict) or "failure-cause" in operation or not isinstance(location, str) or not location.startswith("file:///state/savepoints/") or any(ord(ch)<32 for ch in location):
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
