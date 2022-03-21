
from . import runtime

def render_sql(settings, restore=None):
    sql = "\n".join(path.read_text() for path in sorted((runtime.ROOT / "sql").glob("[0-9]*.sql")))
    password = settings["POSTGRES_PASSWORD"]
    sql = sql.replace("${POSTGRES_PASSWORD}", password.replace("'", "''"))
    if restore:
        if not restore.startswith("file:///state/savepoints/") or "'" in restore or "\n" in restore:
            raise ValueError("restore path must be a local lab savepoint")
        sql = "SET 'execution.savepoint.path' = '" + restore + "';\n" + sql
    return sql

def submit(restore=None):
    from .config import load_env
    import os
    folder = runtime.ROOT / ".runtime"
    folder.mkdir(mode=0o700, exist_ok=True)
    path = folder / "pipeline.sql"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.write(render_sql(load_env(runtime.ROOT / ".env"), restore))
    return runtime.compose("exec", "-T", "jobmanager", "/opt/flink/bin/sql-client.sh", "-f", "/runtime/pipeline.sql", timeout=180)

def initialize_serving():
    for statement in (runtime.ROOT / "sql/clickhouse.sql").read_text().split(";"):
        if statement.strip():
            runtime.clickhouse(statement)
