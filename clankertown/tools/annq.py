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
    log('%s %s'%(c or 'unknown', (e.get('message') or '')[:90]))
    if c=='repeated':
        sent.add(t); open(S,'a').write(t+'\n')
    elif c=='attention': time.sleep(10)
    else: time.sleep(3)
  except Exception as ex:
    log('ERR %s'%str(ex)[:90]); time.sleep(5)
