import glob, time, os

SRC_DIR = os.path.expanduser("")
OUT_PATH = os.path.expanduser("")

def main():
    positions = {}
    while True:
        for path in glob.glob(f"{SRC_DIR}/events-*.jsonl"):
            pos = positions.get(path, 0)
            with open(path, "r") as f:
                f.seek(pos)
                new_lines = f.readlines()
                positions[path] = f.tell()
            if new_lines:
                with open(OUT_PATH, "a") as out:
                    out.writelines(new_lines)
        time.sleep(5)

if __name__ == "__main__":
    main()
