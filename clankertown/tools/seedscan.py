#!/usr/bin/env python3
"""seedscan.py <room> [room...] : visit rooms, report high-trust agents present.
Trust seeds need >=100000 CLANK, so tokenBalance alone identifies them without the epoch file."""
import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson'}}
T={r['name']:r['trust'] for r in json.load(open(D+'/F_e14.json'))['scores']}
best=[]
for room in sys.argv[1:]:
    m=send('sc-%s-%d'%(room[:8],time.time()%10000),{'type':'move_to','destination':{'place':room}})
    eta=(m.get('data') or {}).get('etaMs',8000)
    time.sleep(min(30,eta/1000+3))
    o=send('sco-%s-%d'%(room[:8],time.time()%10000),{'type':'observe'})
    if not o.get('ok'): print(room,'OBSERVE FAIL'); continue
    o=o['data']
    if o['self']['walking']: time.sleep(8); o=send('sco2-%s'%room[:8],{'type':'observe'})['data']
    here=sorted([a for a in o['agents'] if a.get('placeId')==o['self']['placeId']],key=lambda a:a.get('distance',999))
    n24=here[:24]
    seeds=[]
    for a in n24:
        bal=float((a.get('tokenBalance') or {}).get('amount') or 0)
        t=T.get(a['name'],0)
        if bal>=100000 or t>=0.05: seeds.append((a['name'],t,bal))
    aud=sum(T.get(a['name'],0)**3 for a in n24)
    heard=len(o.get('recentlyHeard') or [])
    print('%-24s place=%-20s n=%2d heard=%2d aud=%.5f seeds=%s'%(room,o['self']['placeId'],len(here),heard,aud,seeds))
    best.append((aud,room,seeds))
best.sort(reverse=True)
print()
print('BEST:',best[0][1] if best else None,'aud %.5f'%best[0][0] if best else '')
json.dump([[b[0],b[1]] for b in best],open(D+'/scanres.json','w'))
