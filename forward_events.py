import sys, json, datetime

OUT_PATH = "/home/sufia/IS/ddos-lab/data/events.jsonl"  

def get_pod_info(process):
    pod = process.get("pod", {})
    return pod.get("namespace", ""), pod.get("name", ""), pod.get("workload", "")

def parse_line(line):
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        return None

    now = datetime.datetime.utcnow().isoformat()

    if "process_exec" in ev:
        p = ev["process_exec"]["process"]
        parent = ev["process_exec"].get("parent", {}).get("binary", "")
        ns, pod_name, workload = get_pod_info(p)
        return {
            "timestamp": ev.get("time", now),
            "pod_name": pod_name,
            "namespace": ns,
            "workload": workload,
            "replica_set": workload,   # Tetragon's "workload" = owning Deployment name
            "event_type": "execve",
            "dst_ip": None, "dst_port": None, "bytes": None,
            "proc_name": p.get("binary", ""),
            "proc_args": p.get("arguments", ""),
            "parent_proc": parent,
        }

    if "process_kprobe" in ev:
        pk = ev["process_kprobe"]
        p = pk["process"]
        parent = pk.get("parent", {}).get("binary", "")
        ns, pod_name, workload = get_pod_info(p)
        func = pk.get("function_name", "")
        args = pk.get("args", [])
        dst_ip, dst_port = None, None
        for a in args:
            sock = a.get("sock_arg")
            if sock:
                dst_ip = sock.get("daddr")
                dst_port = sock.get("dport")
        return {
            "timestamp": ev.get("time", now),
            "pod_name": pod_name,
            "namespace": ns,
            "workload": workload,
            "replica_set": workload,
            "event_type": func,       # tcp_connect / tcp_sendmsg / udp_sendmsg
            "dst_ip": dst_ip, "dst_port": dst_port, "bytes": None,
            "proc_name": p.get("binary", ""),
            "proc_args": p.get("arguments", ""),
            "parent_proc": parent,
        }

    return None  # ignore process_exit and anything else

def main():
    with open(OUT_PATH, "a") as out:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            parsed = parse_line(line)
            if parsed:
                out.write(json.dumps(parsed) + "\n")
                out.flush()

if __name__ == "__main__":
    main()
