
import base64, hashlib, json, os, time, uuid
from .runtime import validate_topic

def encode_record(topic, partition, offset, key, value):
    def encode(value):
        return None if value is None else base64.b64encode(value).decode("ascii")
    return {"topic": validate_topic(topic), "partition": partition, "offset": offset,
            "key": encode(key), "value": encode(value)}

def decode_record(record):
    def decode(value):
        return None if value is None else base64.b64decode(value, validate=True)
    return decode(record["key"]), decode(record["value"])

def payload_digest(records):
    return hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def bundle(records, end_offsets):
    return {"format_version": 1, "record_count": len(records), "end_offsets": {str(k): v for k, v in end_offsets.items()},
            "sha256": payload_digest(records), "records": records}

def verify_bundle(value):
    if value.get("format_version") != 1 or value.get("record_count") != len(value.get("records", [])):
        raise ValueError("invalid replay bundle version or count")
    records = value["records"]
    if len(records) > 10000 or payload_digest(records) != value.get("sha256"):
        raise ValueError("replay bundle checksum or limit violation")
    return records
