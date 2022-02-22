
from pathlib import Path
import subprocess, json, urllib.request, urllib.error, time
ROOT = Path(__file__).resolve().parents[1]

def command(args, input=None, timeout=120):
    result = subprocess.run(args, cwd=ROOT, input=input, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        raise RuntimeError("command failed (exit %s): %s" % (result.returncode, result.stderr[-3000:]))
    return result.stdout

def compose(*args, input=None, timeout=120):
    return command(["docker", "compose", "-p", "cdc-2022-validation", *args], input, timeout)

def http_json(url, data=None, method=None, timeout=15):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, body, {"Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read(1024 * 1024 + 1)
    if len(payload) > 1024 * 1024:
        raise ValueError("operator response exceeded 1 MiB")
    return json.loads(payload) if payload else None

def wait_for(predicate, timeout=120, interval=1):
    end = time.monotonic() + timeout
    last = None
    while time.monotonic() < end:
        try:
            value = predicate()
            if value:
                return value
        except (OSError, RuntimeError, ValueError) as exc:
            last = type(exc).__name__
        time.sleep(min(interval, max(0, end - time.monotonic())))
    raise TimeoutError("condition did not converge" + (": " + last if last else ""))
