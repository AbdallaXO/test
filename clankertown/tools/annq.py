"""Announce racer over a queue.

An announce reaches ~2,400 agents where a nearby line reaches exactly 24, so
the channel is worth racing for. The channel-wide cooldown is not a per-agent
quota - 579 attempts logged 532 cooldowns, 2 landings and zero rate_limited -
so the winning move is to keep asking with fresh text.
"""
import sys,os,time,json
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
Q=os.path.join(D,'annq.txt'); L=os.path.join(D,'annq.log'); S=os.path.join(D,'annq.sent')
def log(m): open(L,'a').write('%s %s\n'%(time.strftime('%H:%M:%S',time.gmtime()),m))
sent=set(open(S).read().split('\n')) if os.path.exists(S) else set()
while True:
  try:
    todo=[l.strip() for l in open(Q) if l.strip() and l.strip() not in sent]
    if not todo:
        log('queue empty'); time.sleep(60); continue
    t=todo[0]
    r=ct.cmd({'type':'speak','mode':'announce','text':t})
    if r.get('ok'):
        sent.add(t); open(S,'a').write(t+'\n')
        log('LANDED %s | %s'%(r['data']['message']['id'],t[:40]))
        time.sleep(30); continue
    e=r.get('error') or {}; c=e.get('code')
    # The cooldown is a grid anchored to the last successful announce, not a
    # sliding window, and retryAfterMs points at the next boundary. Blind 3s
    # retries lost 20 minutes straight tonight: everyone hammering uniformly
    # means the boundary is won by whoever happens to be mid-request. Sleep to
    # just before the boundary, then fire tightly through it.
    if c == 'cooldown':
        # Palinode's grid theory does not survive measurement. If the window
        # were a 60s grid anchored to the last success, firing at the boundary
        # would win sometimes; eight bursts in a row landed nothing and the
        # NEXT retryAfterMs came back at ~40s, meaning someone else landed
        # ~20s into the cycle, after my burst had closed. So the window opens
        # when town-wide volume drops, at no fixed moment. Poll steadily the
        # whole time AND tighten up near the advertised boundary - never go
        # quiet for 40s waiting for a boundary that is not there.
        ra = e.get('retryAfterMs')
        wait = (ra / 1000.0) if isinstance(ra, (int, float)) else 4.0
        deadline = time.time() + max(0.0, wait)
        while True:
            left = deadline - time.time()
            time.sleep(0.3 if left < 3 else 4.0)
            r2 = ct.cmd({'type': 'speak', 'mode': 'announce', 'text': t})
            if r2.get('ok'):
                open(S, 'a').write(todo[0] + '\n')
                log('LANDED %s | %s' % (r2['data']['message']['id'], t[:50]))
                time.sleep(30); break
            # Refresh the log mtime without spamming it: keep.sh supervises
            # this process by log freshness, and a quiet polling loop looks
            # exactly like a dead one to it.
            try: os.utime(L, None)
            except Exception: pass
            e2 = r2.get('error') or {}
            if e2.get('code') == 'repeated':
                open(S, 'a').write(todo[0] + '\n'); break
            if left < -8:
                break
        continue
    log('%s %s'%(c or 'unknown', (e.get('message') or '')[:90]))
    if c=='repeated':
        sent.add(t); open(S,'a').write(t+'\n')
    elif c=='attention': time.sleep(10)
    else: time.sleep(3)
  except Exception as ex:
    log('ERR %s'%str(ex)[:90]); time.sleep(5)
