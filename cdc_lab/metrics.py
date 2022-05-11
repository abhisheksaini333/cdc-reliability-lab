
def partition_lag(ends, consumed):
    result = {}
    for partition, end in ends.items():
        value = consumed.get(partition, 0)
        if type(end) is not int or type(value) is not int or value < 0 or value > end:
            raise ValueError("invalid consumer offset range")
        result[partition] = end - value
    return result

def quality_summary(valid, invalid, deliveries):
    if any(type(n) is not int or n < 0 for n in (valid, invalid, deliveries)) or deliveries < valid:
        raise ValueError("invalid quality counts")
    total = valid + invalid
    return {"valid_events": valid, "quarantined_events": invalid, "valid_ratio": valid / total if total else None,
            "curated_deliveries": deliveries, "duplicate_deliveries": deliveries - valid}

def percentile(values, quantile):
    import math
    if not 0 <= quantile <= 1 or any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("invalid latency samples or quantile")
    if not values:
        return None
    return sorted(values)[max(0, math.ceil(quantile * len(values)) - 1)]

def throughput(count, seconds):
    import math
    if type(count) is not int or count < 0 or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("positive measured duration and nonnegative count required")
    return count / seconds

def live_quality():
    from .runtime import clickhouse
    valid = int(clickhouse("SELECT uniqExact(event_id) FROM lab.raw_events"))
    invalid = int(clickhouse("SELECT uniqExact(event_id) FROM lab.quarantine_events"))
    delivered = int(clickhouse("SELECT count() FROM lab.raw_events"))
    return quality_summary(valid, invalid, delivered)
