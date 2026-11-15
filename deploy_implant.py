import subprocess, sys, time, json, datetime

def deploy(pod, namespace, implant_path, label_path):
    t_cp_start = datetime.datetime.utcnow().isoformat()
    subprocess.run(
        ["kubectl", "cp", implant_path, f"{namespace}/{pod}:/tmp/sysupdate", "-n", namespace],
        check=True
    )
    t_cp_end = datetime.datetime.utcnow().isoformat()

    t_chmod_start = datetime.datetime.utcnow().isoformat()
    subprocess.run(
        ["kubectl", "exec", "-n", namespace, pod, "--", "chmod", "+x", "/tmp/sysupdate"],
        check=True
    )
    t_chmod_end = datetime.datetime.utcnow().isoformat()

    t_exec_start = datetime.datetime.utcnow().isoformat()
    subprocess.Popen(["kubectl", "exec", "-n", namespace, pod, "--", "/tmp/sysupdate"])
    t_exec_launched = datetime.datetime.utcnow().isoformat()

    record = {
        "pod": pod,
        "namespace": namespace,
        "implant": implant_path,
        "cp_start": t_cp_start,
        "cp_end": t_cp_end,
        "chmod_start": t_chmod_start,
        "chmod_end": t_chmod_end,
        "exec_start": t_exec_start,
        "exec_launched": t_exec_launched,
    }
    with open(label_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    print(f"Deployed to {namespace}/{pod}: cp={t_cp_start}->{t_cp_end}, "
          f"chmod={t_chmod_start}->{t_chmod_end}, exec_launched={t_exec_launched}")

if __name__ == "__main__":
    pod, ns, implant, label_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    deploy(pod, ns, implant, label_path)
