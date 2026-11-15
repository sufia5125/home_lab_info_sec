import http.server, socketserver, socket, time, random, json, os, datetime

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

def redis_incr():
    s = socket.create_connection(("db-shop", 6379), timeout=2)
    msg = b"*2\r\n$4\r\nINCR\r\n$5\r\ncount\r\n"
    s.sendall(msg)
    log_event("tcp_connect", "db-shop", 6379, len(msg))
    s.recv(1024)
    s.close()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            redis_incr()
        except Exception:
            pass
        time.sleep(random.uniform(0.01, 0.05))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    def log_message(self, *args): pass

with socketserver.TCPServer(("", 8000), Handler) as httpd:
    httpd.serve_forever()
