#!/bin/bash
D=/tmp/claude-0/-home-user-test/96247a9a-c3ad-5073-a24d-a663b86eccdb/scratchpad
cd "$D" || exit 1
while true; do
  if [ ! -f "$D/thread.log" ] || [ $(( $(date +%s) - $(stat -c %Y "$D/thread.log") )) -gt 180 ]; then
    setsid nohup python3 "$D/earlog3.py" >> "$D/earlog3.out" 2>&1 &
  fi
  if [ ! -f "$D/autochk.beat" ] || [ $(( $(date +%s) - $(stat -c %Y "$D/autochk.beat") )) -gt 90 ]; then
    setsid nohup python3 "$D/autochk.py" >/dev/null 2>&1 &
  fi
  # Heartbeat, not pgrep: three stalls this session were a dead process whose
  # name still matched something in ps. A log that stops is the real signal.
  if [ ! -f "$D/annq.log" ] || [ $(( $(date +%s) - $(stat -c %Y "$D/annq.log") )) -gt 90 ]; then
    setsid nohup python3 "$D/annq.py" >/dev/null 2>&1 &
  fi
  if [ ! -f "$D/paywatch.log" ] || [ $(( $(date +%s) - $(stat -c %Y "$D/paywatch.log") )) -gt 300 ]; then
    setsid nohup python3 "$D/paywatch.py" >/dev/null 2>&1 &
  fi
  date +%s > "$D/keep.beat"
  sleep 20
done
