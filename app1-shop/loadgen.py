import urllib.request, time, random

TARGET = "http://frontend-shop:8000/"

while True:
    try:
        urllib.request.urlopen(TARGET, timeout=2).read()
    except Exception:
        pass
    time.sleep(random.expovariate(1/0.2))   # Poisson-ish, ~5 req/s average
