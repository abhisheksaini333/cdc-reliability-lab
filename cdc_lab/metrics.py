
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
