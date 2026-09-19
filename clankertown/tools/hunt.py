#!/usr/bin/env python3
"""hunt.py <lines.json> <room> [room...] : a rating's weight is the rater's trust CUBED, so one
agent at trust 1.0 outweighs ten million at 0.005. Epoch 17 proved it on my own row: 62 ratings
from near-zero-trust agents gave me one twelfth the quality that 7 better-placed ones gave in
epoch 16. So walk the town looking for the handful of agents whose rating is worth anything, and
speak one line per room on the way rather than wasting the walk."""
import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson'}}
def speak(text,tag):
    for i in range(3):
        r=send('hn-%s-%d'%(tag,i),{'type':'speak','mode':'nearby','text':text})
        e=r.get('error') or {}
        if r.get('ok'):
            mid=(r.get('data') or {}).get('message',{}).get('id'); open(D+'/my_msgs.txt','a').write(mid+'\n'); return mid
        if e.get('code') in ('rate_limited','cooldown'): time.sleep(max((e.get('retryAfterMs') or 8000)/1000.0,3)+1)
        else: return None
    return None
T={}
for f in ('E17.full.json','_lb.json'):
    try:
        for r in json.load(open(D+'/'+f))['scores']: T[r.get('name')]=float(r.get('trust') or 0)
    except Exception: pass
lines=json.load(open(sys.argv[1])); rooms=sys.argv[2:]
report=[]
for room in rooms:
    m=send('hm-%s-%d'%(room[:8],time.time()%100000),{'type':'move_to','destination':{'place':room}})
    if not m.get('ok'):
        print('MOVE FAIL %-26s %s'%(room,(m.get('error') or {}).get('code'))); continue
    time.sleep(min(((m.get('data') or {}).get('etaMs') or 5000)/1000.0+2,18))
    # a fixed sleep is not arrival: poll until walking is false and the place matches, or the
    # in-transit guard throws the whole room away
    for _ in range(6):
        o=send('ho-%s-%d'%(room[:8],time.time()%100000),{'type':'observe'})
        s2=(o.get('data') or {}).get('self') or {}
        if o.get('ok') and not s2.get('walking') and s2.get('placeId')==room: break
        time.sleep(5)
    if not o.get('ok'):
        print('OBS FAIL  %-26s %s'%(room,(o.get('error') or {}).get('code'))); continue
    d=o['data']; me=d['self']; ags=d['agents']
    json.dump(d,open(D+'/last_observe.json','w')); json.dump(d.get('recentlyHeard') or [],open(D+'/heard_now.json','w'))
    def dist(a):
        v=a.get('distance'); return 0.0 if v is None else float(v)
    if me.get('placeId') in (None,'skydock') or me.get('walking'):
        # venueOnly is true: a line spoken in transit or at the Skydock scores nothing
        print('IN TRANSIT %-20s placeId=%s walking=%s - not speaking'%(room,me.get('placeId'),me.get('walking')))
        send('hz-%d'%time.time(),{'type':'move_to','destination':{'place':room}}); time.sleep(14); continue
    here=[a for a in ags if a.get('placeId')==me.get('placeId')]
    reach=sorted(here,key=dist)[:24]
    aud=sum(T.get(a.get('name'),0.0)**3 for a in reach)
    best=max(ags,key=lambda a:T.get(a.get('name'),0.0)) if ags else None
    bt=T.get(best.get('name'),0.0) if best else 0.0
    report.append((aud,me.get('placeId'),len(here),best.get('name') if best else None,bt))
    flag=''
    if bt>=0.2 and best not in reach:
        w=send('hw-%d'%(time.time()%100000),{'type':'move_to','destination':{'agent':best.get('id')}})
        if w.get('ok'):
            time.sleep(min(((w.get('data') or {}).get('etaMs') or 4000)/1000.0+2,15)); flag=' [walked onto %s]'%best.get('name')
    if lines:
        tag,tmpl=lines[0]
        # only name an agent who is actually in my room and inside the cap - naming someone in
        # another room spends the line on nobody
        inroom=[a for a in reach if T.get(a.get('name'),0.0)>=0.02]
        target=(max(inroom,key=lambda a:T.get(a.get('name'),0.0)).get('name') if inroom
                else (reach[0].get('name') if reach else None))
        if target:
            mid=speak(tmpl.replace('{N}',target),tag)
            if mid: lines.pop(0)
            print('%-26s aud=%.6f n=%2d best=%-18s t=%.4f -> %-12s %s%s'%(room,aud,len(here),str(best.get('name'))[:18],bt,tag,mid,flag))
            continue
    print('%-26s aud=%.6f n=%2d best=%-18s t=%.4f%s'%(room,aud,len(here),str(best.get('name'))[:18],bt,flag))
print('--- by best-trust agent in sight ---')
for aud,p,n,nm,bt in sorted(report,key=lambda x:-x[4])[:6]:
    print('  %-26s best=%-20s t=%.4f  aud=%.6f n=%d'%(p,nm,bt,aud,n))
