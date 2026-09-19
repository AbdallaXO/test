#!/usr/bin/env python3
"""fire.py <jsonfile> : [[tag,targetName,text],...] - observe ONCE, then for each line send it
only if the named target can actually hear it (quiet when d<=2, broadcast when inside the
nearest-24 cap). Distances go stale between observe and send, so quiet sends fall back to
broadcast on out_of_range instead of being lost."""
import json,subprocess,os,sys,math
D=os.path.dirname(os.path.abspath(__file__))
def send(cid,body,tries=None):
    cmd=[D+'/send.sh',cid,json.dumps(body)]
    r=subprocess.run(cmd,capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson','raw':r.stdout[:120]}}
lines=json.load(open(sys.argv[1]))
o=send('fobs-%s'%sys.argv[1][:6],{'type':'observe'})
if not o.get('ok'): print('OBSERVE FAILED',o.get('error')); sys.exit(1)
d=o['data']; me=d['self']; ags=d['agents']
json.dump(d,open(D+'/last_observe.json','w'))
def dist(a):
    v=a.get('distance')
    return 0.0 if v is None else float(v)
ranked=sorted([a for a in ags if a.get('placeId')==me.get('placeId')],key=dist)
rank={a.get('name'):i for i,a in enumerate(ranked)}
byname={a.get('name'):a for a in ags}
print('place=%s ratingsLeft=%s agents=%d'%(me.get('placeId'),me.get('ratingsLeft'),len(ags)))
for tag,target,text in lines:
    a=byname.get(target)
    if a is None: print('SKIP %-16s %s not in room'%(tag,target)); continue
    dd=dist(a); rk=rank.get(target,999)
    # broadcast reaches the target AND 23 others inside the cap, so prefer it; quiet only
    # for a target outside the nearest-24 but within 2 tiles (rule: 0 is a legal distance)
    if rk<24 and a.get('inEarshot',True):
        body={'type':'speak','mode':'nearby','text':text}
    elif a.get('inQuietRange') or dd<=2:
        body={'type':'speak','mode':'quiet','to':(a.get('agentId') or a.get('id')),'text':text}
    else:
        print('SKIP %-16s %s rank=%d d=%.1f unreachable'%(tag,target,rk,dd)); continue
    r=send('f17-%s'%tag,body)
    if not r.get('ok') and r.get('error',{}).get('code')=='out_of_range':
        r=send('f17-%s-b'%tag,{'type':'speak','mode':'nearby','text':text})
    if r.get('ok'):
        mid=(r.get('data') or {}).get('message',{}).get('id')
        open(D+'/my_msgs.txt','a').write(mid+'\n')
        print('OK   %-16s -> %-16s d=%.1f rank=%d %s'%(tag,target,dd,rk,mid))
    else:
        print('FAIL %-16s -> %-16s %s'%(tag,target,r.get('error')))
