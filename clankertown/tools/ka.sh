#!/bin/bash
# ka.sh [minutes] : keepalive. Rule 7 - inTown goes false after ~40s of no commands, and the
# town is now at its population cap so a lost slot is not cheap to get back. Send a cheap
# observe every 25s so analysis turns never idle me out.
D=/tmp/claude-0/-home-user-test/da23c3a0-e8fc-5ac5-a9bb-df5c9af8464a/scratchpad/clankertown
cd "$D" || exit 1
M=${1:-60}
END=$(( $(date +%s) + M*60 ))
while [ "$(date +%s)" -lt "$END" ]; do
  R=$(./send.sh "ka-$(date +%s)" '{"type":"observe"}')
  echo "$(date -u +%H:%M:%S) $(echo "$R" | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    print('in' if d.get('ok') else d.get('error',{}).get('code','?'))
except Exception: print('nojson')")"
  sleep 25
done
