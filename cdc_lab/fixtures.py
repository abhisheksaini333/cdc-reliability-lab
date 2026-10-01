
def devices(count=3):
    if type(count) is not int or not 1 <= count <= 10000:
        raise ValueError("device count must be between 1 and 10000")
    return [{"id": i, "site": ("north", "south", "west")[(i - 1) % 3]} for i in range(1, count + 1)]

def validate_range(count, start):
    if type(count) is not int or not 0 <= count <= 1000000 or type(start) is not int or not 1 <= start <= 9223372036854775807 or start + max(count-1,0) > 9223372036854775807:
        raise ValueError("invalid reading count or starting identity range")

def readings(count=20, seed=17, device_count=3, start=1):
    import random
    validate_range(count, start)
    devices(device_count)
    rng = random.Random(seed)
    return [{"id": i, "device_id": rng.randint(1, device_count), "value": round(rng.uniform(-10, 45), 3), "unit": "C"}
            for i in range(start, start + count)]

def events(rows, operation="r", start_lsn=1000):
    if operation not in ("r", "c", "u", "d"):
        raise ValueError("unsupported operation")
    return [{"op": operation, "source": {"name": "lab", "schema": "public", "table": "readings", "lsn": start_lsn + n},
             "before": dict(value) if operation == "d" else None,
             "after": None if operation == "d" else dict(value)} for n, value in enumerate(rows)]
