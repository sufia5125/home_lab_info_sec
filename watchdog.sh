#!/bin/bash
export KUBECONFIG="$HOME/.kube/config"
LOGFILE="$HOME/IS/ddos-lab/data/watchdog.log"
DATA_DIR="$HOME/IS/ddos-lab/data"
LAB_DIR="$HOME/IS/ddos-lab"

log() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $1" >> "$LOGFILE"
}

# --- 1. Check Tetragon pod health ---
TETRAGON_STATUS=$(kubectl get pods -n kube-system -l app.kubernetes.io/name=tetragon -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
TETRAGON_READY=$(kubectl get pods -n kube-system -l app.kubernetes.io/name=tetragon -o jsonpath='{.items[0].status.containerStatuses[*].ready}' 2>/dev/null)

if [[ "$TETRAGON_STATUS" != "Running" || "$TETRAGON_READY" == *"false"* ]]; then
    log "ALERT: Tetragon pod unhealthy (status=$TETRAGON_STATUS, ready=$TETRAGON_READY)"
    kubectl get pods -n kube-system -l app.kubernetes.io/name=tetragon >> "$LOGFILE" 2>&1
    kubectl describe pods -n kube-system -l app.kubernetes.io/name=tetragon | tail -20 >> "$LOGFILE" 2>&1
else
    log "OK: Tetragon healthy"
fi

# --- 2. Check the three forwarder/disturbance processes are alive ---
check_process() {
    NAME=$1
    if ! pgrep -f "$NAME" > /dev/null; then
        log "ALERT: $NAME is NOT running, restarting"
        return 1
    else
        log "OK: $NAME running"
        return 0
    fi
}

if ! check_process "run_events_forwarder.sh"; then
    nohup "$LAB_DIR/run_events_forwarder.sh" >> "$DATA_DIR/forwarder_stdout.log" 2>&1 &
    disown
    log "ACTION: restarted run_events_forwarder.sh"
fi

if ! check_process "forward_k8s_events.py"; then
    nohup python3 "$LAB_DIR/forward_k8s_events.py" >> "$DATA_DIR/k8s_forwarder_stdout.log" 2>&1 &
    disown
    log "ACTION: restarted forward_k8s_events.py"
fi

if ! check_process "disturbance.py"; then
    nohup python3 "$LAB_DIR/disturbance.py" >> "$DATA_DIR/disturbance_stdout.log" 2>&1 &
    disown
    log "ACTION: restarted disturbance.py"
fi

# --- 3. Check data files are actually GROWING, not just processes existing ---
check_growth() {
    FILE=$1
    LABEL=$2
    if [[ ! -f "$FILE" ]]; then
        log "ALERT: $LABEL missing entirely"
        return
    fi
    SIZE_NOW=$(wc -l < "$FILE")
    SIZE_FILE="$DATA_DIR/.${LABEL}_last_count"
    if [[ -f "$SIZE_FILE" ]]; then
        SIZE_PREV=$(cat "$SIZE_FILE")
        if [[ "$SIZE_NOW" -le "$SIZE_PREV" ]]; then
            log "ALERT: $LABEL has NOT grown since last check ($SIZE_PREV -> $SIZE_NOW lines)"
        else
            log "OK: $LABEL grew ($SIZE_PREV -> $SIZE_NOW lines)"
        fi
    fi
    echo "$SIZE_NOW" > "$SIZE_FILE"
}

check_growth "$DATA_DIR/events.jsonl" "events"
check_growth "$DATA_DIR/k8s_events.jsonl" "k8s_events"
# disturbances.jsonl grows slowly (every 20-40 min) so skip growth-check false alarms for it

# --- 4. Disk space check ---
USAGE=$(df "$HOME" | tail -1 | awk '{print $5}' | tr -d '%')
if [[ "$USAGE" -gt 85 ]]; then
    log "ALERT: disk usage at ${USAGE}%"
fi

log "---- watchdog cycle complete ----"
