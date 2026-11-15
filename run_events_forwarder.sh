#!/bin/bash
while true; do
    echo "[$(date -u)] Starting Tetragon log stream..."
    kubectl logs -n kube-system ds/tetragon -c export-stdout -f | python3 ~/IS/ddos-lab/forward_events.py
    echo "[$(date -u)] Stream ended, reconnecting in 5s..."
    sleep 5
done
