import subprocess, random, json, time, datetime

OUT_PATH = "" 

DEPLOYMENTS = [
    ("app1", "frontend-shop"),
    ("app1", "api-shop"),
    ("app2", "worker"),
]

def log_event(kind, detail):
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "disturbance_type": kind,
        "detail": detail,
    }
    with open(OUT_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    print(record)

def rolling_restart():
    ns, dep = random.choice(DEPLOYMENTS)
    subprocess.run(["kubectl", "rollout", "restart", f"deployment/{dep}", "-n", ns])
    log_event("rolling_restart", f"{ns}/{dep}")

def scale_updown():
    ns, dep = random.choice(DEPLOYMENTS)
    original = 4
    temp = random.choice([3, 5])
    subprocess.run(["kubectl", "scale", f"deployment/{dep}", "-n", ns, f"--replicas={temp}"])
    log_event("scale", f"{ns}/{dep} -> {temp}")
    time.sleep(60)
    subprocess.run(["kubectl", "scale", f"deployment/{dep}", "-n", ns, f"--replicas={original}"])
    log_event("scale", f"{ns}/{dep} -> {original} (restored)")

def exec_debug():
    ns, dep = random.choice(DEPLOYMENTS)
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", ns, "-l", f"app={dep}", "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True
    )
    pod = result.stdout.strip()
    if pod:
        subprocess.run(["kubectl", "exec", "-n", ns, pod, "--", "ls", "/"])
        log_event("exec_debug", f"{ns}/{pod}")

def load_spike():
    log_event("load_spike_start", "app1/loadgen-shop rate increased 3-5x")
    subprocess.run([
        "kubectl", "patch", "deployment", "loadgen-shop", "-n", "app1",
        "--type=json",
        "-p=[{\"op\":\"replace\",\"path\":\"/spec/template/spec/volumes/0/configMap/name\",\"value\":\"loadgen-shop-script-spike\"}]"
    ])
    subprocess.run(["kubectl", "rollout", "restart", "deployment/loadgen-shop", "-n", "app1"])
    subprocess.run(["kubectl", "rollout", "status", "deployment/loadgen-shop", "-n", "app1", "--timeout=60s"])

    time.sleep(180)  

    subprocess.run([
        "kubectl", "patch", "deployment", "loadgen-shop", "-n", "app1",
        "--type=json",
        "-p=[{\"op\":\"replace\",\"path\":\"/spec/template/spec/volumes/0/configMap/name\",\"value\":\"loadgen-shop-script\"}]"
    ])
    subprocess.run(["kubectl", "rollout", "restart", "deployment/loadgen-shop", "-n", "app1"])
    log_event("load_spike_end", "app1/loadgen-shop rate restored to normal")
    
ACTIONS = [rolling_restart, scale_updown, exec_debug, load_spike]

def main():
    while True:
        wait_min = random.uniform(10, 20)
        time.sleep(wait_min * 60)
        action = random.choice(ACTIONS)
        try:
            action()
        except Exception as e:
            log_event("error", str(e))

if __name__ == "__main__":
    main()
