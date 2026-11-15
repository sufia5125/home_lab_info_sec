import time, random
TARGET = "http://frontend-shop:8000/"
import urllib.request
while True:
    try:
        urllib.request.urlopen(TARGET, timeout=2).read()
    except Exception:
        pass
    time.sleep(random.expovariate(1/0.05))  # ~5x faster than normal 0.2s mean
