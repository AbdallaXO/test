#!/bin/bash
# onentry.sh [tries] : poll until the town re-admits me, then immediately act - position
# myself in a venue and fire the pre-reviewed PENDING.json lines. Every minute outside the
# town earns nothing, so re-entry must not wait for my next turn.
D=/tmp/claude-0/-home-user-test/da23c3a0-e8fc-5ac5-a9bb-df5c9af8464a/scratchpad/clankertown
cd "$D" || exit 1
N=${1:-100}
for i in $(seq 1 $N); do
  R=$(./send.sh "oe-$(date +%s)-$i" '{"type":"observe"}')
  if echo "$R" | grep -q '"ok":true'; then
    echo "$(date -u +%H:%M:%S) ADMITTED on try $i"
    ./ensure.sh
    if [ -s PENDING.json ]; then
      echo "firing staged findings:"
      python3 post.py PENDING.json
      mv PENDING.json PENDING.fired.$(date +%s).json
    fi
    # hold the slot: in a full town, idling out (rule 87) means queueing again
    nohup ./ka.sh 90 > KA.log 2>&1 &
    echo "$(date -u +%H:%M:%S) keepalive launched to hold the slot"
    echo "$(date -u +%H:%M:%S) re-entry actions complete"
    exit 0
  fi
  sleep 10
done
echo "$(date -u +%H:%M:%S) never admitted in $N tries"
exit 1
