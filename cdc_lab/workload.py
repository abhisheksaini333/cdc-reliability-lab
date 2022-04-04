
from .runtime import sql_literal

def insert_sql(rows):
    if not rows or len(rows) > 10000:
        raise ValueError("batch must contain 1 through 10000 rows")
    tuples = []
    for row in rows:
        if type(row.get("id")) is not int or row["id"] <= 0 or type(row.get("device_id")) is not int or row["device_id"] <= 0:
            raise ValueError("positive integer reading and device identities required")
        tuples.append("(" + ",".join(sql_literal(row[k]) for k in ("id", "device_id", "value", "unit")) + ")")
    return "INSERT INTO readings(id,device_id,value,unit) VALUES " + ",".join(tuples) + " ON CONFLICT(id) DO UPDATE SET device_id=EXCLUDED.device_id,value=EXCLUDED.value,unit=EXCLUDED.unit;"
