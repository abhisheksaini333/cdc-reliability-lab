
def positive_identity(value):
    import re
    if isinstance(value, str) and re.fullmatch(r"[1-9][0-9]*", value):
        value = int(value)
    if type(value) is not int or not 1 <= value <= 9223372036854775807:
        raise ValueError("invalid analytical identity")
    return value

def canonical(rows):
    import math
    result = {}
    for row in rows:
        key = positive_identity(row["id"])
        if key in result:
            raise ValueError("duplicate current-state key")
        try:
            value = float(row.get("reading_value", row.get("value")))
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid analytical numeric value") from exc
        if not math.isfinite(value):
            raise ValueError("nonfinite analytical value")
        result[key] = {"id": key, "device_id": positive_identity(row["device_id"]), "value": round(value, 9),
                       "unit": row["unit"], "site": row["site"]}
    return [result[key] for key in sorted(result)]

def compare(expected, actual):
    left = {row["id"]: row for row in canonical(expected)}
    right = {row["id"]: row for row in canonical(actual)}
    missing = sorted(left.keys() - right.keys())
    extra = sorted(right.keys() - left.keys())
    changed = sorted(key for key in left.keys() & right.keys() if left[key] != right[key])
    return {"equivalent": not (missing or extra or changed), "expected_count": len(left), "actual_count": len(right),
            "missing": missing, "extra": extra, "changed": changed}

def digest(rows):
    import hashlib, json
    return hashlib.sha256(json.dumps(canonical(rows), sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def source_rows():
    from .runtime import postgres
    import json
    sql = "SELECT coalesce(json_agg(t),'[]'::json) FROM (SELECT r.id,r.device_id,r.value,r.unit,d.site FROM readings r JOIN devices d ON d.id=r.device_id WHERE r.value BETWEEN -80 AND 150 AND r.unit='C' ORDER BY r.id) t;"
    return json.loads(postgres(sql))

def served_rows():
    from .runtime import clickhouse
    import json
    return [json.loads(line) for line in clickhouse("SELECT * FROM lab.current_readings ORDER BY id FORMAT JSONEachRow").splitlines()]

def live():
    return compare(source_rows(), served_rows())
