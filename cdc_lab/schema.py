
import json
from .contracts import validate_schema
from .runtime import postgres

def normalize_types(rows):
    mapping = {"bigint": "bigint", "double precision": "double", "text": "text"}
    return {row["column_name"]: mapping.get(row["data_type"], row["data_type"]) for row in rows}

def inspect_schema():
    sql = "SELECT json_agg(t) FROM (SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='readings') t;"
    return normalize_types(json.loads(postgres(sql)))

def preflight():
    errors = validate_schema(inspect_schema())
    if errors:
        raise ValueError("source schema incompatible: " + ", ".join(errors))
    return {"compatible": True}
