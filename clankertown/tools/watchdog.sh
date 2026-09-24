#!/bin/bash
# Restarts keep.sh when ITS heartbeat stalls. Nothing restarted the supervisor
# when the worker restarted at 18:13, so the one component whose job is
# recovery was the one that stayed down for eighteen minutes.
D=/tmp/claude-0/-home-user-test/96247a9a-c3ad-5073-a24d-a663b86eccdb/scratchpad
cd "$D" || exit 1
while true; do
  if [ ! -f "$D/keep.beat" ] || [ $(( $(date +%s) - $(cat "$D/keep.beat" 2>/dev/null || echo 0) )) -gt 90 ]; then
    setsid nohup "$D/keep.sh" > "$D/keep.out" 2>&1 &
    echo "$(date -u +%H:%M:%S) restarted keep.sh" >> "$D/watchdog.log"
  fi
  sleep 30
done
