
def unique(events):
    result = {}
    for event in events:
        key = event["event_id"]
        if key in result and result[key] != event:
            raise ValueError("conflicting payload for one logical event identity")
        result[key] = dict(event)
    return list(result.values())
