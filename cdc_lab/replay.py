
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

def validate_offsets(records, end_offsets):
    seen = {}
    topic = None
    for record in records:
        validate_topic(record["topic"])
        topic = topic or record["topic"]
        partition, offset = record["partition"], record["offset"]
        if topic != record["topic"] or type(partition) is not int or partition < 0 or type(offset) is not int or offset < 0:
            raise ValueError("invalid replay coordinates")
        end = end_offsets.get(str(partition))
        if type(end) is not int or offset >= end or offset <= seen.get(partition, -1):
            raise ValueError("replay offsets are unordered or outside frozen bounds")
        seen[partition] = offset
        decode_record(record)
        decode_headers(record)

def write_bundle(path, value):
    verify_bundle(value)
    validate_offsets(value["records"], value["end_offsets"])
    data = json.dumps(value, sort_keys=True, indent=2).encode()
    if len(data) > 16 * 1024 * 1024:
        raise ValueError("replay archive exceeds 16 MiB")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)

def read_bundle(path):
    with open(path, "rb") as handle:
        data = handle.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024:
        raise ValueError("replay archive exceeds 16 MiB")
    value = json.loads(data)
    verify_bundle(value)
    validate_offsets(value["records"], value["end_offsets"])
    return value

def replay_group(label="export"):
    validate_topic(label)
    return "cdc-replay-" + label[:40] + "-" + uuid.uuid4().hex

def export_topic(topic, maximum=10000, timeout=30):
    from kafka import KafkaConsumer, TopicPartition
    validate_topic(topic)
    if type(maximum) is not int or not 1 <= maximum <= 10000:
        raise ValueError("invalid export record limit")
    consumer = KafkaConsumer(bootstrap_servers="127.0.0.1:4702", group_id=replay_group(),
                             enable_auto_commit=False, auto_offset_reset="earliest", request_timeout_ms=15000,
                             api_version=(3, 0, 0))
    try:
        partitions = consumer.partitions_for_topic(topic)
        if not partitions:
            raise ValueError("source topic has no partitions")
        assigned = [TopicPartition(topic, p) for p in sorted(partitions)]
        consumer.assign(assigned)
        ends = consumer.end_offsets(assigned)
        consumer.seek_to_beginning(*assigned)
        records = []
        deadline = time.monotonic() + timeout
        while any(consumer.position(p) < ends[p] for p in assigned):
            if time.monotonic() > deadline:
                raise TimeoutError("bounded export did not reach its frozen offsets")
            for partition, messages in consumer.poll(timeout_ms=500, max_records=500).items():
                for record in messages:
                    if record.offset < ends[partition]:
                        records.append(encode_with_headers(topic, record.partition, record.offset, record.key, record.value, record.headers))
                        if len(records) > maximum:
                            raise ValueError("export exceeds record limit")
        records.sort(key=lambda r: (r["partition"], r["offset"]))
        return bundle(records, {p.partition: end for p, end in ends.items()})
    finally:
        consumer.close()

def replay_target(topic):
    validate_topic(topic)
    if topic not in ("lab.curated", "lab.public.readings") and not topic.startswith("lab.replay."):
        raise ValueError("replay target must be an explicit lab data topic")
    return topic

def publish(value, target):
    from kafka import KafkaProducer
    target = replay_target(target)
    records = verify_bundle(value)
    validate_offsets(records, value["end_offsets"])
    validate_publish_headers(records)
    producer = KafkaProducer(bootstrap_servers="127.0.0.1:4702", acks="all", retries=3,
                             max_block_ms=15000, request_timeout_ms=15000, api_version=(3, 0, 0))
    try:
        for record in records:
            key, data = decode_record(record)
            producer.send(target, key=key, value=data, partition=record["partition"], headers=decode_headers(record)).get(timeout=20)
        producer.flush(timeout=20)
    finally:
        producer.close(timeout=20)
    return len(records)

def encode_with_headers(topic, partition, offset, key, value, headers):
    record = encode_record(topic, partition, offset, key, value)
    record["headers"] = [[name, None if item is None else base64.b64encode(item).decode("ascii")] for name, item in headers]
    return record

def decode_headers(record):
    headers = record.get("headers", [])
    if not isinstance(headers, list) or len(headers) > 100:
        raise ValueError("invalid replay header list")
    result = []
    for pair in headers:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2 or not isinstance(pair[0], str) or not 1 <= len(pair[0]) <= 255:
            raise ValueError("invalid replay header name")
        name, value = pair
        result.append((name, None if value is None else base64.b64decode(value, validate=True)))
    return result

def validate_publish_headers(records):
    # kafka-python 2.0.2 cannot serialize nullable header values, although Kafka can.
    # Refuse the complete archive before writing rather than silently changing bytes.
    for record in records:
        if any(value is None for _, value in decode_headers(record)):
            raise ValueError("nullable headers require a Kafka client with nullable-header support; archive preserved")
