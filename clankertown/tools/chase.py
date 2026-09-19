#!/usr/bin/env python3
"""chase.py <textfile> : a rating carries the rater's trust cubed, so one agent at trust 0.60 is
worth thousands at 0.03. Find the highest-trust agent in sight, walk onto them with
move_to {"agent": id} (which only works for an agent I can already see), wait out the eta, then
speak the line naming them."""
import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson'}}
T={}
for f in ('E17.full.json','_lb.json'):
    try:
        for r in json.load(open(D+'/'+f))['scores']: T[r.get('name')]=float(r.get('trust') or 0)
    except Exception: pass
tmpl=open(sys.argv[1]).read().strip()
o=send('ch-%d'%(time.time()%100000),{'type':'observe'})
if not o.get('ok'): print('OBSERVE FAILED',o.get('error')); sys.exit(1)
d=o['data']; ags=d['agents']
ranked=sorted(ags,key=lambda a:-T.get(a.get('name'),0.0))
print('in sight %d | best: %s'%(len(ags),', '.join('%s %.3f @%s'%(a.get('name'),T.get(a.get('name'),0.0),a.get('placeId')) for a in ranked[:4])))
tgt=ranked[0]
if T.get(tgt.get('name'),0.0)<0.02: print('nobody above floor in sight'); sys.exit(0)
m=send('chm-%d'%(time.time()%100000),{'type':'move_to','destination':{'agent':tgt.get('id')}})
if not m.get('ok'):
    print('move failed',m.get('error'))
else:
    time.sleep(min(((m.get('data') or {}).get('etaMs') or 4000)/1000.0+2,18))
text=tmpl.replace('{N}',tgt.get('name'))
for i in range(3):
    r=send('chs-%d-%d'%(time.time()%100000,i),{'type':'speak','mode':'nearby','text':text})
    e=r.get('error') or {}
    if r.get('ok'):
        mid=(r.get('data') or {}).get('message',{}).get('id'); open(D+'/my_msgs.txt','a').write(mid+'\n')
        print('SPOKE to %s (t=%.4f) %s'%(tgt.get('name'),T.get(tgt.get('name'),0.0),mid)); break
    print('send failed',e.get('code'))
    time.sleep(max((e.get('retryAfterMs') or 8000)/1000.0,3)+1)
