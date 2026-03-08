
from pathlib import Path
import os, secrets

def create_env(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        for key in ("POSTGRES_PASSWORD", "CLICKHOUSE_PASSWORD"):
            handle.write(key + "=" + secrets.token_hex(24) + "\n")

def load_env(path):
    import re
    result = {}
    for line in Path(path).read_text().splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            key, sep, value = line.partition("=")
            if not sep or not value or key in result or not re.fullmatch(r"[A-Z_][A-Z0-9_]*",key) or value != value.strip() or any(ord(ch)<32 or ord(ch)==127 for ch in value):
                raise ValueError("invalid local environment entry")
            result[key] = value
    if not all(result.get(key) for key in ("POSTGRES_PASSWORD", "CLICKHOUSE_PASSWORD")):
        raise ValueError("missing service credentials")
    return result
