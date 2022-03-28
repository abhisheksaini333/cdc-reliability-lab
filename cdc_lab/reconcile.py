
def canonical(rows):
    import math
    result = {}
    for row in rows:
        key = int(row["id"])
        if key in result:
            raise ValueError("duplicate current-state key")
        value = float(row.get("reading_value", row.get("value")))
        if not math.isfinite(value):
            raise ValueError("nonfinite analytical value")
        result[key] = {"id": key, "device_id": int(row["device_id"]), "value": round(value, 9),
                       "unit": row["unit"], "site": row["site"]}
    return [result[key] for key in sorted(result)]
