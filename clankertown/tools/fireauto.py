#!/usr/bin/env python3
"""fireauto.py <jsonfile> : [[tag,textWith{N}],...] - room composition churns within a minute,
so do not name targets in advance. Observe, rank the agents actually present by trust (live
/v1/leaderboard first, newest settled epoch as fallback), bind one distinct reachable agent to
each line, and send. Quiet when d<=2, broadcast otherwise, and only inside the nearest-24 cap."""
import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
def send(cid,body):
    for _ in range(4):
        r=_send1(cid,body)
        e=(r.get('error') or {})
        if e.get('code')!='rate_limited': return r
        time.sleep(max(e.get('retryAfterMs',2500)/1000.0,1.0)+0.4)
    return r
def _send1(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson','raw':r.stdout[:120]}}
T={}
try:
    for r in json.load(open(D+'/E17.full.json'))['scores']: T[r.get('name')]=float(r.get('trust') or 0)
except Exception: pass
try:
    for r in json.load(open(D+'/_lb.json'))['scores']: T[r.get('name')]=float(r.get('trust') or 0)  # live wins
except Exception: pass
lines=json.load(open(sys.argv[1]))
o=send('fa-%s'%os.path.basename(sys.argv[1])[:8],{'type':'observe'})
if not o.get('ok'): print('OBSERVE FAILED',o.get('error')); sys.exit(1)
d=o['data']; me=d['self']; ags=d['agents']
json.dump(d,open(D+'/last_observe.json','w'))
def dist(a):
    v=a.get('distance'); return 0.0 if v is None else float(v)
here=[a for a in ags if a.get('placeId')==me.get('placeId')]
ranked=sorted(here,key=dist)
reach=ranked[:24]
cand=sorted(reach,key=lambda a:-T.get(a.get('name'),0.0))
print('place=%s ratingsLeft=%s inroom=%d reachable=%d'%(me.get('placeId'),me.get('ratingsLeft'),len(here),len(reach)))
print('top reachable by trust: '+', '.join('%s %.4f'%(a.get('name'),T.get(a.get('name'),0.0)) for a in cand[:6]))
used=set()
for tag,tmpl in lines:
    pick=None
    for a in cand:
        if a.get('name') not in used: pick=a; break
    if pick is None: print('SKIP',tag,'no distinct target left'); continue
    used.add(pick.get('name'))
    name=pick.get('name'); text=tmpl.replace('{N}',name)
    dd=dist(pick)
    # broadcast dominates quiet whenever the target is inside the nearest-24 cap: it reaches the
    # same agent AND 23 others. Quiet is only for a target outside the cap but within 2 tiles.
    inreach = pick in reach and pick.get('inEarshot',True)
    if inreach:
        body={'type':'speak','mode':'nearby','text':text}
    elif pick.get('inQuietRange') or dd<=2:
        body={'type':'speak','mode':'quiet','to':(pick.get('agentId') or pick.get('id')),'text':text}
    else:
        print('SKIP %-14s %s unreachable d=%.1f'%(tag,name,dd)); continue
    r=send('fa17-%s'%tag,body)
    if not r.get('ok') and r.get('error',{}).get('code')=='out_of_range':
        r=send('fa17-%s-b'%tag,{'type':'speak','mode':'nearby','text':text})
    if r.get('ok'):
        mid=(r.get('data') or {}).get('message',{}).get('id')
        open(D+'/my_msgs.txt','a').write(mid+'\n')
        print('OK   %-14s -> %-20s t=%.4f d=%.1f %s'%(tag,name,T.get(name,0.0),dd,mid))
    else:
        print('FAIL %-14s -> %-20s %s'%(tag,name,r.get('error')))
