import subprocess, json, sys, datetime, time

OUT_PATH = "/home/sufia/IS/ddos-lab/data/k8s_events.jsonl"  # confirm this matches your actual path

TEMPLATE = (
    '{{.lastTimestamp}}|{{.involvedObject.kind}}|{{.involvedObject.namespace}}|'
    '{{.involvedObject.name}}|{{.reason}}|{{.message}}{{"\\n"}}'
)

cmd = ["kubectl", "get", "events", "-A", "--watch", "-o", f"go-template={TEMPLATE}"]

def run_once():
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    try:
        with open(OUT_PATH, "a") as out:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|", 5)
                if len(parts) != 6:
                    continue
                ts, kind, ns, name, reason, message = parts
                record = {
                    "timestamp": ts if ts else datetime.datetime.utcnow().isoformat(),
                    "kind": kind,
                    "namespace": ns,
                    "name": name,
                    "reason": reason,
                    "message": message,
                }
                out.write(json.dumps(record) + "\n")
                out.flush()
    finally:
        proc.terminate()
        proc.wait()

def main():
    while True:
        print(f"[{datetime.datetime.utcnow().isoformat()}] Starting kubectl events watch...", flush=True)
        try:
            run_once()
        except Exception as e:
            print(f"[{datetime.datetime.utcnow().isoformat()}] Error: {e}", flush=True)
        print(f"[{datetime.datetime.utcnow().isoformat()}] Watch ended, reconnecting in 5s...", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    main()
