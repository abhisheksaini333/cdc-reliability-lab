
from .runtime import sql_literal

def insert_sql(rows):
    if not rows or len(rows) > 10000:
        raise ValueError("batch must contain 1 through 10000 rows")
    tuples = []
    seen = set()
    for row in rows:
        if type(row.get("id")) is not int or row["id"] <= 0 or type(row.get("device_id")) is not int or row["device_id"] <= 0:
            raise ValueError("positive integer reading and device identities required")
        if row["id"] in seen:
            raise ValueError("duplicate reading identity in source batch")
        seen.add(row["id"])
        tuples.append("(" + ",".join(sql_literal(row[k]) for k in ("id", "device_id", "value", "unit")) + ")")
    return "INSERT INTO readings(id,device_id,value,unit) VALUES " + ",".join(tuples) + " ON CONFLICT(id) DO UPDATE SET device_id=EXCLUDED.device_id,value=EXCLUDED.value,unit=EXCLUDED.unit;"

def update_sql(identity, value):
    if type(identity) is not int or identity <= 0:
        raise ValueError("positive integer reading identity required")
    return "UPDATE readings SET value=" + sql_literal(value) + " WHERE id=" + str(identity) + ";"

def delete_sql(identities):
    if not identities or len(identities) > 10000 or any(type(key) is not int or key <= 0 for key in identities):
        raise ValueError("bounded positive integer identities required")
    return "DELETE FROM readings WHERE id IN (" + ",".join(str(key) for key in sorted(set(identities))) + ");"

def batches(rows, size=100):
    if type(size) is not int or not 1 <= size <= 10000:
        raise ValueError("invalid batch size")
    for offset in range(0, len(rows), size):
        yield rows[offset:offset + size]

def generate(count=100, seed=17, start=1000):
    from .fixtures import readings
    from .runtime import postgres
    rows = readings(count, seed, start=start)
    for batch in batches(rows):
        postgres(insert_sql(batch))
    return len(rows)
