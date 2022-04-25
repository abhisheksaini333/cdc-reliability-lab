
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

def sql_literal(value):
    import math
    if value is None:
        return "NULL"
    if type(value) in (int, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite SQL numeric literal")
        return str(value)
    if not isinstance(value, str) or "\x00" in value:
        raise ValueError("unsupported SQL literal")
    return "'" + value.replace("'", "''") + "'"

def postgres(sql):
    return compose("exec", "-T", "postgres", "psql", "-X", "-U", "lab", "-d", "lab", "-v", "ON_ERROR_STOP=1", "-At", input=sql)

def clickhouse(sql):
    from .config import load_env
    import base64
    secret = load_env(ROOT / ".env")["CLICKHOUSE_PASSWORD"]
    request = urllib.request.Request("http://127.0.0.1:4705/?database=lab", data=sql.encode())
    request.add_header("Authorization", "Basic " + base64.b64encode(("lab:" + secret).encode()).decode())
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(16 * 1024 * 1024).decode()

def connector_config(env_path=None):
    from .config import load_env
    settings = load_env(env_path or ROOT / ".env")
    config = json.loads((ROOT / "infra/connect/source.json").read_text())
    config["config"]["database.password"] = settings["POSTGRES_PASSWORD"]
    return config

def register_connector():
    config = connector_config()
    return http_json("http://127.0.0.1:4703/connectors/" + config["name"] + "/config", config["config"], "PUT")

def validate_topic(value):
    import re
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9._-]{0,248}", value) or value in (".", ".."):
        raise ValueError("invalid Kafka topic")
    return value

def create_topic(name):
    return compose("exec", "-T", "-e", "KAFKA_HEAP_OPTS=-Xms32m -Xmx96m", "kafka", "/kafka/bin/kafka-topics.sh", "--bootstrap-server", "kafka:9092", "--create", "--if-not-exists", "--topic", validate_topic(name), "--partitions", "1", "--replication-factor", "1")
