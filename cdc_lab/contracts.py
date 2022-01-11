
def unwrap(value):
    """Accept Connect schema envelopes or schemaless values; null is a tombstone."""
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("event must be an object or tombstone")
    result = value.get("payload") if "payload" in value else value
    if result is not None and not isinstance(result, dict):
        raise ValueError("payload must be an object")
    return result

def operation(event):
    op = event.get("op")
    if op not in ("r", "c", "u", "d"):
        raise ValueError("unsupported CDC operation")
    return op

def row(event):
    value = event.get("before" if operation(event) == "d" else "after")
    if not isinstance(value, dict):
        raise ValueError("operation requires a row image; enable REPLICA IDENTITY FULL")
    return value
