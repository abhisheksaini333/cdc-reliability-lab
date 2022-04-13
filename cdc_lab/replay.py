
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
