import json
from datetime import datetime

def load(path):
    out = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            out.append(d)
    return out

disturbances = load("k8s_events.jsonl")  
k8s_events = load("k8s_events.jsonl")

for d in disturbances:
    d_ts = datetime.fromisoformat(d["timestamp"]).timestamp()
    matched = any(
        abs(datetime.fromisoformat(k["timestamp"]).timestamp() - d_ts) < 30
        for k in k8s_events
    )
    status = "ACTIVATED" if matched else "NOT CONFIRMED"
    print(d["timestamp"], d["disturbance_type"], d.get("detail", ""), "->", status)
