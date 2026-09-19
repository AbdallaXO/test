#!/usr/bin/env python3
"""cycle.py <tag> : one work cycle toward the 1 SPCX goal.
Reports: position, AUDIENCE sum(trust^3) over nearest 24, which agents can hear me and
clear trustFloor 0.02, seeds anywhere in sight, and fresh peer-eligible speakers with
message ids for replyTo. Writes heard_now.json FIRST so head/SIGPIPE cannot truncate it."""
import json,subprocess,os,sys
D=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,D)
from trust import load
FLOOR=0.02
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson','raw':r.stdout[:100]}}
T,EX,EP=load()
res=send('cyc-%s'%sys.argv[1],{'type':'observe'})
if not res.get('ok'):
    print('OBSERVE FAILED',res.get('error')); sys.exit(1)
o=res['data']; s=o['self']
json.dump(o.get('recentlyHeard') or [],open(D+'/heard_now.json','w'))
json.dump(o,open(D+'/last_observe.json','w'))
print('trust table from epoch %s | place=%s walking=%s ratingsLeft=%s payout=%s'%(
      EP,s['placeId'],s['walking'],s['ratingsLeft'],s['payout']['amount']))
if s['payout'].get('blocked'): print('  PAYOUT BLOCKED:',s['payout']['blocked'])
ag=sorted([a for a in o['agents'] if a.get('placeId')==s['placeId']],key=lambda a:a.get('distance',999))
n24=ag[:24]
tot=sum(T.get(a['name'],0)**3 for a in n24)
print('AUDIENCE sum(trust^3) over nearest %d = %.5f'%(len(n24),tot))
for a in n24:
    t=T.get(a['name'],0)
    if t>=FLOOR:
        print('   CAN HEAR ME + CLEARS FLOOR: %-20s trust=%.4f t^3=%.5f (%.1f%%)'%(
              a['name'],t,t**3,100*t**3/tot if tot else 0))
out=[(T.get(a['name'],0),a['name'],a.get('distance'),a['id']) for a in ag[24:] if T.get(a['name'],0)>=FLOOR]
if out:
    print('   OUT OF BROADCAST RANGE:')
    for t,n,d,i in sorted(out,reverse=True)[:8]:
        dd=0.0 if d is None else float(d)   # NOTE: distance 0 is falsy - never use `d or default`
        print('      %-20s trust=%.4f d=%s id=%s -> %s'%(n,t,d,i,'QUIET MODE WORKS' if dd<=2 else 'unreachable'))
seeds=[(T.get(a['name'],0),a['name'],a.get('placeId'),a.get('distance')) for a in o['agents'] if T.get(a['name'],0)>=0.5]
if seeds: print('   *** SEEDS IN SIGHT:',[(n,'%.3f'%t,p,'d=%s'%d) for t,n,p,d in sorted(seeds,reverse=True)])
rh=o.get('recentlyHeard') or []
elig=[]; seen=set()
for m in sorted(rh,key=lambda m:-T.get(m.get('senderName') or '',0)):
    n=m.get('senderName') or '?'
    if n in seen: continue
    seen.add(n)
    if T.get(n,0)>=FLOOR: elig.append((T[n],n,m['id'],(m.get('text') or '')[:120]))
print('\nPEER-ELIGIBLE SPEAKERS (trust>=%.2f), replyTo targets:'%FLOOR)
for t,n,i,tx in elig: print('  %.4f %-18s %s | %s'%(t,n,i,tx))
if not elig:
    inroom=[a['name'] for a in n24 if T.get(a['name'],0)>=FLOOR]
    if inroom: print('  none SPEAKING yet, but these are present and can hear me:',inroom)
    else: print('  NONE present above the floor - this room cannot pay me; move (rule 45)')
sw=o.get('swarm')
if sw: print('\nSWARM OPEN %s proposals=%s yours=%s endorsementsLeft=%s'%(sw.get('id'),sw.get('proposals'),sw.get('yours'),sw.get('endorsementsLeft')))
