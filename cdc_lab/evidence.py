
import json, os, uuid
from pathlib import Path

def record_run(folder, results):
    data = json.dumps(results, indent=2, allow_nan=False) + "\n"
    folder = Path(folder)
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = folder / ("run-" + uuid.uuid4().hex + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink()
        raise
    return path
