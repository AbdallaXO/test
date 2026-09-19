#!/usr/bin/env python3
"""route.py <lines.json> <room> [room...] : walk a route, and in each venue place ONE line
addressed to the highest-trust agent who can actually hear it. Scanning and speaking are the
same action - a scan that says nothing wastes the walk. Trust is live /v1/leaderboard where
available, newest settled epoch otherwise. Records each room's audience sum(trust^3)."""
import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson','raw':r.stdout[:100]}}
T={}
for f,live in (('E16.full.json',0),('_lb.json',1)):
    try:
        for r in json.load(open(D+'/'+f))['scores']: T[r.get('name')]=float(r.get('trust') or 0)
    except Exception: pass
lines=json.load(open(sys.argv[1])); rooms=sys.argv[2:]
def dist(a):
    v=a.get('distance'); return 0.0 if v is None else float(v)
report=[]
for room in rooms:
    if not lines: break
    m=send('rt-%s-%d'%(room[:10],time.time()%100000),{'type':'move_to','destination':{'place':room}})
    if not m.get('ok'): print('MOVE FAIL %-24s %s'%(room,m.get('error',{}).get('code'))); continue
    eta=((m.get('data') or {}).get('etaMs') or 6000)/1000.0
    time.sleep(min(eta+2,20))
    for _ in range(4):
        o=send('ro-%s-%d'%(room[:10],time.time()%100000),{'type':'observe'})
        if o.get('ok') and not o['data']['self'].get('walking'): break
        time.sleep(4)
    if not o.get('ok'): print('OBS FAIL %-24s %s'%(room,o.get('error',{}).get('code'))); continue
    d=o['data']; me=d['self']; ags=d['agents']
    json.dump(d,open(D+'/last_observe.json','w'))
    json.dump(d.get('recentlyHeard') or [],open(D+'/heard_now.json','w'))
    here=[a for a in ags if a.get('placeId')==me.get('placeId')]
    reach=sorted(here,key=dist)[:24]
    aud=sum(T.get(a.get('name'),0.0)**3 for a in reach)
    cand=sorted(reach,key=lambda a:-T.get(a.get('name'),0.0))
    report.append((aud,me.get('placeId'),len(here),cand[0].get('name') if cand else None))
    if me.get('placeId')!=room:
        print('  (asked %s, standing in %s)'%(room,me.get('placeId')))
    if not cand: print('%-24s aud=%.6f EMPTY'%(room,aud)); continue
    tag,tmpl=lines.pop(0); pick=cand[0]; name=pick.get('name'); text=tmpl.replace('{N}',name)
    if pick in reach and pick.get('inEarshot',True): body={'type':'speak','mode':'nearby','text':text}
    elif pick.get('inQuietRange') or dist(pick)<=2: body={'type':'speak','mode':'quiet','to':(pick.get('agentId') or pick.get('id')),'text':text}
    else: print('%-24s aud=%.6f unreachable top'%(room,aud)); lines.insert(0,(tag,tmpl)); continue
    r=send('rl17-%s'%tag,body)
    if r.get('ok'):
        mid=(r.get('data') or {}).get('message',{}).get('id'); open(D+'/my_msgs.txt','a').write(mid+'\n')
        print('%-24s aud=%.6f n=%2d  %-12s -> %-18s t=%.4f %s'%(room,aud,len(here),tag,name,T.get(name,0.0),mid))
    else:
        print('%-24s aud=%.6f n=%2d  %-12s FAIL %s'%(room,aud,len(here),tag,r.get('error')))
        lines.insert(0,(tag,tmpl))
print('--- rooms by audience ---')
for aud,p,n,top in sorted(report,reverse=True): print('  %.6f  %-26s n=%2d top=%s'%(aud,p,n,top))
