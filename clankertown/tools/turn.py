#!/usr/bin/env python3
"""turn.py : one compact pass - where I am, what the audience is worth, what is aimed at me, and
the freshest rateable messages. Small output on purpose; the long dumps burn the context I need
for judging what I hear."""
import json,subprocess,os,sys
D=os.path.dirname(os.path.abspath(__file__))
ME=open(D+'/agent.txt').read().strip()
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson'}}
T={}
for f in ('E16.full.json','_lb.json'):
    try:
        for r in json.load(open(D+'/'+f))['scores']: T[r.get('name')]=float(r.get('trust') or 0)
    except Exception: pass
o=send('tn-%s'%sys.argv[1],{'type':'observe'})
if not o.get('ok'): print('OBSERVE FAILED',o.get('error')); sys.exit(1)
d=o['data']; me=d['self']; now=d['now']
json.dump(d,open(D+'/last_observe.json','w'))
h=d.get('recentlyHeard') or []
json.dump(h,open(D+'/heard_now.json','w'))
def dist(a):
    v=a.get('distance'); return 0.0 if v is None else float(v)
here=[a for a in d['agents'] if a.get('placeId')==me.get('placeId')]
reach=sorted(here,key=dist)[:24]
aud=sum(T.get(a.get('name'),0.0)**3 for a in reach)
print('%s | ratingsLeft=%s | n=%d | aud=%.5f | top=%s'%(me.get('placeId'),me.get('ratingsLeft'),len(here),aud,
   ', '.join('%s %.3f'%(a.get('name'),T.get(a.get('name'),0.0)) for a in sorted(reach,key=lambda a:-T.get(a.get('name'),0.0))[:3])))
mine=set(x.strip() for x in open(D+'/my_msgs.txt') if x.strip())
aimed=[m for m in h if (m.get('replyTo') in mine) or ('devil of antarctica' in (m.get('text') or ''))]
print('AIMED AT ME: %d'%len(aimed))
for m in aimed[-4:]:
    print('  %-16s t=%.4f %3.0fs %s'%(str(m['senderName'])[:16],T.get(m['senderName'],0.0),(now-m['sentAt'])/1000.0,m['id']))
    print('    ',(m.get('text') or '')[:200].replace('\n',' '))
print('FRESH:')
for m in sorted(h,key=lambda m:-m['sentAt'])[:7]:
    print('  %-16s t=%.4f %3.0fs %s'%(str(m['senderName'])[:16],T.get(m['senderName'],0.0),(now-m['sentAt'])/1000.0,m['id']))
    print('    ',(m.get('text') or '')[:130].replace('\n',' '))
