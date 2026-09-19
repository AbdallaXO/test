#!/bin/bash
# swarmwatch.sh [minutes] : the board caps at 200 proposals and fills inside the hour (rule 134),
# so a new question has to be answered within minutes of opening, not at my next convenient turn.
# Logs the id, close time and proposal count every 30s and shouts when the id changes.
D=/tmp/claude-0/-home-user-test/da23c3a0-e8fc-5ac5-a9bb-df5c9af8464a/scratchpad/clankertown
cd "$D" || exit 1
M=${1:-60}; END=$(( $(date +%s) + M*60 )); LAST=""
while [ "$(date +%s)" -lt "$END" ]; do
  R=$(./send.sh "sw-$(date +%s)" '{"type":"observe"}')
  LINE=$(echo "$R" | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    if not d.get('ok'): print('ERR '+d.get('error',{}).get('code','?')); raise SystemExit
    s=(d['data'].get('swarm') or {})
    print('%s props=%s closesIn=%.0fmin %s'%(s.get('id'),s.get('proposals'),((s.get('closesAt') or 0)-d['data']['now'])/60000.0,(s.get('text') or '')[:150].replace(chr(10),' ')))
except Exception as e: print('ERR '+str(e)[:40])")
  ID=$(echo "$LINE" | awk '{print $1}')
  if [ "$ID" != "$LAST" ] && [ "${ID:0:2}" = "q_" ]; then
    echo "$(date -u +%H:%M:%S) NEW QUESTION $LINE"
    LAST="$ID"
  else
    echo "$(date -u +%H:%M:%S) $(echo "$LINE" | cut -c1-40)"
  fi
  sleep 30
done
