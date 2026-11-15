import subprocess, json, datetime, re

IFACE = "cni0"  # confirm this matches Step 2's output
OUT_PATH = "/home/sufia/IS/ddos-lab/data/network_capture.jsonl"

def get_pod_ip_map():
    out = subprocess.run(
        ["kubectl", "get", "pods", "-A", "-o",
         "jsonpath={range .items[*]}{.status.podIP} {.metadata.name} {.metadata.namespace}{\"\\n\"}{end}"],
        capture_output=True, text=True
    ).stdout
    mapping = {}
    for line in out.strip().split("\n"):
        parts = line.split()
        if len(parts) == 3:
            mapping[parts[0]] = (parts[1], parts[2])
    return mapping

def main():
    proc = subprocess.Popen(
        ["sudo", "tcpdump", "-i", IFACE, "-n", "-l", "tcp or udp"],
        stdout=subprocess.PIPE, text=True
    )
    pod_map = get_pod_ip_map()
    refresh_counter = 0
    with open(OUT_PATH, "a") as out:
        for line in proc.stdout:
            refresh_counter += 1
            if refresh_counter % 200 == 0:
                pod_map = get_pod_ip_map()  # periodically refresh pod IPs
            m = re.search(r"IP (\S+)\.(\d+) > (\S+)\.(\d+)", line)
            if not m:
                continue
            src_ip, src_port, dst_ip, dst_port = m.groups()
            pod_name, ns = pod_map.get(src_ip, ("unknown", "unknown"))
            record = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "pod_name": pod_name,
                "namespace": ns,
                "src_ip": src_ip, "src_port": src_port,
                "dst_ip": dst_ip, "dst_port": dst_port,
                "event_type": "tcp_connect",
            }
            out.write(json.dumps(record) + "\n")
            out.flush()

if __name__ == "__main__":
    main()
