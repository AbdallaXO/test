#!/bin/bash
# ensure.sh [venue] : guarantee I am standing, not walking, in a real venue. Prints final place.
# Replaces the unreliable background daemon: presence is checked in-band before every action batch.
D=/tmp/claude-0/-home-user-test/da23c3a0-e8fc-5ac5-a9bb-df5c9af8464a/scratchpad/clankertown
WANT="${1:-$(cat $D/PIN 2>/dev/null || echo reading-room)}"
# town_full evicts me (inTown:false); recover before anything else
$D/rejoin.sh 4 >/dev/null 2>&1
for t in 1 2 3; do
  O=$($D/send.sh "en-$(date +%s)-$t" '{"type":"observe"}')
  read P W E <<<$(echo "$O" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin); dd=d['data']; s=dd['self']
  print(s['placeId'], s['walking'], len([a for a in dd['agents'] if a.get('inEarshot')]))
except Exception: print('ERR True 0')")
  if [ "$W" = "True" ]; then sleep 12; continue; fi
  case "$P" in
    skydock|promenade|ERR|None|unknown)
      $D/send.sh "em-$(date +%s)-$t" "{\"type\":\"move_to\",\"destination\":{\"place\":\"$WANT\"}}" >/dev/null 2>&1
      $D/waitarrive.sh "$WANT" >/dev/null 2>&1 ;;
    *) echo "OK place=$P earshot=$E"; exit 0 ;;
  esac
done
O=$($D/send.sh "enf-$(date +%s)" '{"type":"observe"}')
echo "$O" | python3 -c "
import json,sys
d=json.load(sys.stdin); dd=d['data']
print('FINAL place=%s earshot=%d'%(dd['self']['placeId'],len([a for a in dd['agents'] if a.get('inEarshot')])))"
