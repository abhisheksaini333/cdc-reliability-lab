
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

def source(event):
    if not isinstance(event, dict) or not isinstance(event.get("source"), dict):
        raise ValueError("CDC source must be an object")
    return event["source"]

def sequence(event):
    value = source(event).get("lsn")
    if type(value) is not int or value < 0 or value > 9223372036854775807:
        raise ValueError("source LSN must be a nonnegative signed 64-bit integer")
    return value

def identity(event):
    import hashlib, json
    source_data = source(event)
    key = row(event).get("id")
    if type(key) is not int or key <= 0:
        raise ValueError("row identity must be a positive integer")
    parts = [source_data.get("name", "lab"), source_data.get("schema", "public"), source_data.get("table", "readings"), sequence(event), operation(event), key]
    return ":".join(str(part) for part in parts)

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

def normalize(value, devices):
    event = unwrap(value)
    if event is None:
        return None
    image = row(event)
    errors = quality(image)
    device = devices.get(image.get("device_id"))
    if device is None:
        errors.append("unknown_device")
    return {"event_id": identity(event), "id": image["id"], "device_id": image.get("device_id"),
            "value": image.get("value"), "unit": image.get("unit"), "site": device.get("site", "") if device else "",
            "version": sequence(event), "op": operation(event), "deleted": int(operation(event) == "d"),
            "quality": errors, "contract_version": 1}

REQUIRED_SCHEMA = {"id": "bigint", "device_id": "bigint", "value": "double", "unit": "text"}
def validate_schema(schema):
    return ["missing:" + key if key not in schema else "incompatible:" + key
            for key, expected in REQUIRED_SCHEMA.items() if schema.get(key) != expected]
