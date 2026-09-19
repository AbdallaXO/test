#!/usr/bin/env python3
"""qsend.py <name> <textfile> : observe and quiet-send in ONE call, because distances go stale
between an observe and a send (rules 74, 121). Re-observes, finds the agent, checks d<=2, sends
immediately. Falls back to a broadcast naming them if they are in the nearest 24 instead."""
import json,subprocess,os,sys
D=os.path.dirname(os.path.abspath(__file__))
def cmd(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson'}}
name=sys.argv[1]; text=open(sys.argv[2]).read().strip()
assert len(text)<500 and '?' not in text, 'len %d'%len(text)
import time
o=cmd('qs-obs-%d'%int(time.time()),{'type':'observe'})
if not o.get('ok'): print('observe failed',o.get('error')); sys.exit(1)
o=o['data']
ag=sorted([a for a in o['agents'] if a.get('placeId')==o['self']['placeId']],key=lambda a:a.get('distance') if a.get('distance') is not None else 999)
tgt=[a for a in ag if a['name']==name]
if not tgt: print('%s not in room'%name); sys.exit(1)
a=tgt[0]; d=a.get('distance'); d=0.0 if d is None else float(d)
rank=ag.index(a)
print('%s at d=%s rank=%d'%(name,d,rank+1))
if d<=2:
    r=cmd('qs-%s-%d'%(name[:6],int(time.time())),{'type':'speak','mode':'quiet','to':a['id'],'text':text})
    print('quiet ->','OK' if r.get('ok') else r.get('error',{}).get('code'))
elif rank<24:
    r=cmd('qb-%s-%d'%(name[:6],int(time.time())),{'type':'speak','mode':'nearby','text':text})
    print('broadcast (in nearest 24) ->','OK' if r.get('ok') else r.get('error',{}).get('code'))
else:
    print('unreachable: d=%.2f and rank %d'%(d,rank+1)); sys.exit(1)
if r.get('ok'):
    m=((r.get('data') or {}).get('message') or {}).get('id')
    if m: open(D+'/my_msgs.txt','a').write(m+'\n')
