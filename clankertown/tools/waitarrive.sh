#!/bin/bash
# Block until walking:false and placeId matches $1 (or any venue if no arg). Prints final state.
D=/tmp/claude-0/-home-user-test/da23c3a0-e8fc-5ac5-a9bb-df5c9af8464a/scratchpad/clankertown
WANT="$1"
for i in $(seq 1 20); do
  O=$($D/send.sh "wa-$(date +%s)-$i" '{"type":"observe"}')
  R=$(echo "$O" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin)
  if not d.get('ok'): print('ERR',(d.get('error') or {}).get('code'),0); raise SystemExit
  dd=d['data']; s=dd['self']
  print(s['placeId'], s['walking'], len([a for a in dd['agents'] if a.get('inEarshot')]))
except Exception: print('ERR x 0')")
  set -- $R
  P=$1; W=$2; E=$3
  if [ "$W" = "False" ] && [ "$P" != "None" ]; then
    if [ -z "$WANT" ] || [ "$P" = "$WANT" ]; then echo "ARRIVED place=$P earshot=$E"; exit 0; fi
  fi
  sleep 8
done
echo "TIMEOUT place=$P walking=$W earshot=$E"
