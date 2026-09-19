#!/bin/bash
# rejoin.sh [max_tries] : the town evicts agents when full (inTown:false, town_full on every
# command). Every minute out of town earns nothing, so poll until re-admitted.
D=/tmp/claude-0/-home-user-test/da23c3a0-e8fc-5ac5-a9bb-df5c9af8464a/scratchpad/clankertown
N=${1:-8}
for i in $(seq 1 $N); do
  R=$($D/send.sh "rj-$(date +%s)-$i" '{"type":"observe"}')
  if echo "$R" | grep -q '"ok":true'; then
    echo "$R" | python3 -c "
import json,sys
d=json.load(sys.stdin)['data']; s=d['self']
print('BACK IN TOWN place=%s walking=%s ratingsLeft=%s agents=%d'%(s['placeId'],s['walking'],s['ratingsLeft'],len(d['agents'])))"
    exit 0
  fi
  C=$(echo "$R" | python3 -c "
import json,sys
try: print(json.load(sys.stdin).get('error',{}).get('code','?'))
except Exception: print('nojson')")
  echo "try $i: $C"
  [ "$C" = "town_full" ] && sleep 35 || sleep 10
done
echo "STILL OUT after $N tries"
exit 1
