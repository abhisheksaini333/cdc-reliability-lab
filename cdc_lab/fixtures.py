
def devices(count=3):
    if type(count) is not int or not 1 <= count <= 10000:
        raise ValueError("device count must be between 1 and 10000")
    return [{"id": i, "site": ("north", "south", "west")[(i - 1) % 3]} for i in range(1, count + 1)]
