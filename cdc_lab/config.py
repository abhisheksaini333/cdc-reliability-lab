
from pathlib import Path
import os, secrets

def create_env(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        for key in ("POSTGRES_PASSWORD", "CLICKHOUSE_PASSWORD"):
            handle.write(key + "=" + secrets.token_hex(24) + "\n")

def load_env(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        if line and not line.startswith("#"):
            key, sep, value = line.partition("=")
            if not sep or not value or key in result:
                raise ValueError("invalid local environment entry")
            result[key] = value
    if not all(result.get(key) for key in ("POSTGRES_PASSWORD", "CLICKHOUSE_PASSWORD")):
        raise ValueError("missing service credentials")
    return result
