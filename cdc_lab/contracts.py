
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

def sequence(event):
    value = event.get("source", {}).get("lsn")
    if type(value) is not int or value < 0 or value > 9223372036854775807:
        raise ValueError("source LSN must be a nonnegative signed 64-bit integer")
    return value

def identity(event):
    import hashlib, json
    source = event.get("source", {})
    key = row(event).get("id")
    if type(key) is not int or key <= 0:
        raise ValueError("row identity must be a positive integer")
    parts = [source.get("name", "lab"), source.get("schema", "public"), source.get("table", "readings"), sequence(event), operation(event), key]
    return hashlib.sha256(json.dumps(parts, separators=(",", ":")).encode()).hexdigest()

def quality(value):
    import math
    errors = []
    for key in ("id", "device_id"):
        if type(value.get(key)) is not int or value[key] <= 0:
            errors.append("invalid_" + key)
    number = value.get("value")
    if type(number) not in (int, float) or not math.isfinite(number):
        errors.append("invalid_value")
    elif number < -80 or number > 150:
        errors.append("value_out_of_range")
    if value.get("unit") != "C":
        errors.append("unsupported_unit")
    return errors
