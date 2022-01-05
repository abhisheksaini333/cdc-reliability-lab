
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
