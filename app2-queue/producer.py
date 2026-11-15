import socket, time, random, os, json, datetime

POD_NAME = os.environ.get("POD_NAME", "unknown")
LOG_PATH = f"/var/log/app/events-{POD_NAME}.jsonl"

def log_event(event_type, dst_ip=None, dst_port=None, nbytes=None):
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "pod_name": POD_NAME,
        "namespace": os.environ.get("POD_NAMESPACE", "unknown"),
        "workload": os.environ.get("WORKLOAD_NAME", "unknown"),
        "replica_set": os.environ.get("WORKLOAD_NAME", "unknown"),
        "event_type": event_type,
        "dst_ip": dst_ip, "dst_port": dst_port, "bytes": nbytes,
        "proc_name": "python", "proc_args": "", "parent_proc": "",
    }
    try:
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass

def redis_lpush(sock, job_id):
    msg = f"*3\r\n$5\r\nLPUSH\r\n$4\r\njobs\r\n${len(job_id)}\r\n{job_id}\r\n"
    sock.sendall(msg.encode())
    sock.recv(1024)
    log_event("tcp_sendmsg", "redis-queue", 6379, len(msg))

while True:
    s = socket.create_connection(("redis-queue", 6379), timeout=2)
    log_event("tcp_connect", "redis-queue", 6379, 0)
    burst_size = random.randint(3, 10)
    for _ in range(burst_size):
        redis_lpush(s, str(random.randint(1, 1000000)))
        time.sleep(random.uniform(0.05, 0.2))
    s.close()
    time.sleep(random.uniform(5, 20))
