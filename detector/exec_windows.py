import json

def load_exec_windows(disturbances_path, window_pad=20):
    windows = []
    with open(disturbances_path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("disturbance_type") == "exec_debug":
                from datetime import datetime
                ts = datetime.fromisoformat(d["timestamp"]).timestamp()
                windows.append((ts - window_pad, ts + window_pad))
    return windows

def in_exec_window(ts, windows):
    return any(lo <= ts <= hi for lo, hi in windows)
