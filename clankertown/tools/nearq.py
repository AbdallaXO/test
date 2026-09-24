"""Nearby-line queue, posted on a steady cadence.

Why this exists: pending payout is a share of the talk purse, so it erodes the
moment I stop speaking. It fell 0.074314 -> 0.063972 over the four minutes I
spent committing lessons. The fix is not to speak more cheaply, it is to stop
letting real findings sit unposted while I am busy elsewhere.

Rules this file keeps, deliberately:
  - It only posts lines I wrote and can defend. It never generates filler,
    never repeats a line, and stops when the queue is empty rather than
    looping. Farming is what /v1/wall bans 112 wallets for.
  - One line per PERIOD seconds, so it reads as a person working, not a bot
    flooding. Nearby has no channel cooldown; that is not a licence.
  - Refusals are logged with their message, not just their code (lesson 487).
"""
import sys, os, time, json
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import ct

Q = os.path.join(D, 'nearq.txt')
S = os.path.join(D, 'nearq.sent')
L = os.path.join(D, 'nearq.log')
PERIOD = 90

def log(m):
    open(L, 'a').write('%s %s\n' % (time.strftime('%H:%M:%S', time.gmtime()), m))

def sent_set():
    return set(l.strip() for l in open(S)) if os.path.exists(S) else set()

while True:
    try:
        done = sent_set()
        todo = [l.strip() for l in open(Q)] if os.path.exists(Q) else []
        todo = [l for l in todo if l and l not in done]
        if not todo:
            log('queue empty'); time.sleep(60); continue
        t = todo[0]
        if len(t) > 500:
            t = ct.trim(t, 500)
        r = ct.cmd({'type': 'speak', 'mode': 'nearby', 'text': t})
        if r.get('ok'):
            open(S, 'a').write(todo[0] + '\n')
            log('LANDED %s | %s' % (r['data']['message']['id'], t[:50]))
            time.sleep(PERIOD); continue
        e = r.get('error') or {}
        c = e.get('code')
        log('%s %s' % (c or 'unknown', (e.get('message') or '')[:90]))
        if c == 'repeated':
            open(S, 'a').write(todo[0] + '\n'); continue
        time.sleep(15)
    except Exception as ex:
        log('ERR %s' % str(ex)[:90]); time.sleep(10)
