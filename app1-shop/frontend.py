import http.server, socketserver, urllib.request, json, os, datetime, socket

POD_NAME = os.environ.get("POD_NAME", "unknown")
LOG_PATH = f"/var/log/app/events-{POD_NAME}.jsonl"
API_URL = "http://api-shop:8000/"

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

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            dst_ip = socket.gethostbyname("api-shop")
            body = urllib.request.urlopen(API_URL, timeout=2).read()
            log_event("tcp_connect", dst_ip, 8000, len(body))
        except Exception:
            pass
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    def log_message(self, *args): pass

with socketserver.TCPServer(("", 8000), Handler) as httpd:
    httpd.serve_forever()
