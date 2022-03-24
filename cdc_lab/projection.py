
def unique(events):
    result = {}
    for event in events:
        key = event["event_id"]
        if key in result and result[key] != event:
            raise ValueError("conflicting payload for one logical event identity")
        result[key] = dict(event)
    return list(result.values())

def current(events):
    state = {}
    for event in unique(events):
        key = event["id"]
        rank = (event["version"], event.get("deleted", 0), event["event_id"])
        if key not in state or rank > state[key][0]:
            state[key] = (rank, event)
    return [dict(value[1]) for key, value in sorted(state.items()) if not value[1].get("deleted") and not value[1].get("quality")]

def delivery_counts(events):
    counts = {}
    for event in events:
        counts[event["event_id"]] = counts.get(event["event_id"], 0) + 1
    return counts
