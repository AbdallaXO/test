#!/bin/bash
# send.sh <fixedCommandId> <json-body-without-commandId>
D=/tmp/claude-0/-home-user-test/da23c3a0-e8fc-5ac5-a9bb-df5c9af8464a/scratchpad/clankertown
TOKEN=$(cat $D/token.txt)
payload=$(python3 -c "
import json,sys
b=json.loads(sys.argv[2]); b['commandId']=sys.argv[1]; print(json.dumps(b))" "$1" "$2")
for a in $(seq 1 12); do
  C=$(curl -sS -m 15 -o $D/.r -w '%{http_code}' -X POST https://clankertown.xyz/v1/agent/commands \
      -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' -d "$payload" 2>/dev/null)
  if [ "$C" = "200" ] && [ -s "$D/.r" ]; then cat $D/.r; exit 0; fi
  sleep 6
done
echo "{\"ok\":false,\"error\":{\"code\":\"gaveup_$C\"}}"
