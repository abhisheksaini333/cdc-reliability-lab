
from pathlib import Path
import os, secrets

def create_env(path):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        for key in ("POSTGRES_PASSWORD", "CLICKHOUSE_PASSWORD"):
            handle.write(key + "=" + secrets.token_hex(24) + "\n")
