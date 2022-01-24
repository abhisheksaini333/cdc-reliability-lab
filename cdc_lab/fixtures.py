
def devices(count=3):
    if type(count) is not int or not 1 <= count <= 10000:
        raise ValueError("device count must be between 1 and 10000")
    return [{"id": i, "site": ("north", "south", "west")[(i - 1) % 3]} for i in range(1, count + 1)]

def readings(count=20, seed=17, device_count=3, start=1):
    import random
    if type(count) is not int or not 0 <= count <= 1000000 or type(start) is not int or start < 1:
        raise ValueError("invalid reading count or starting identity")
    devices(device_count)
    rng = random.Random(seed)
    return [{"id": i, "device_id": rng.randint(1, device_count), "value": round(rng.uniform(-10, 45), 3), "unit": "C"}
            for i in range(start, start + count)]
