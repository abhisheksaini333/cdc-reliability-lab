
def partition_lag(ends, consumed):
    result = {}
    for partition, end in ends.items():
        value = consumed.get(partition, 0)
        if type(end) is not int or type(value) is not int or value < 0 or value > end:
            raise ValueError("invalid consumer offset range")
        result[partition] = end - value
    return result
