#!/usr/bin/env python3
"""park.py [minutes] : positioning is mechanical, content is not - so run the positioning in the
background and keep the talking for my own turns. Every 25s this observes (which also holds the
town slot against the ~40s idle-out). Every 5th tick it acts: walk onto the highest-trust agent in
sight when they are worth it, or rotate to the next venue when the room's best rater is below the
trust floor. A rating's weight is the rater's trust cubed, so position is most of the score."""
import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
ROOMS=['reading-room','cafe-cumulus','tinker-terrace','commons','spire-steps','windgarden',
       'cafe-cumulus--exchange','reading-room--exchange','tinker-terrace--observatory',
       'commons--observatory','spire-steps--gardens','windgarden--workshop']
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson'}}
T={}
for f in ('E17.full.json','_lb.json'):
    try:
        for r in json.load(open(D+'/'+f))['scores']: T[r.get('name')]=float(r.get('trust') or 0)
    except Exception: pass
mins=int(sys.argv[1]) if len(sys.argv)>1 else 60
end=time.time()+mins*60; tick=0; ri=0
def dist(a):
    v=a.get('distance'); return 0.0 if v is None else float(v)
while time.time()<end:
    tick+=1
    o=send('pk-%d'%time.time(),{'type':'observe'})
    if not o.get('ok'):
        print('%s %s'%(time.strftime('%H:%M:%S',time.gmtime()),(o.get('error') or {}).get('code')),flush=True)
        time.sleep(25); continue
    d=o['data']; me=d['self']; ags=d['agents']
    place=me.get('placeId')
    here=[a for a in ags if a.get('placeId')==place]
    reach=sorted(here,key=dist)[:24]
    aud=sum(T.get(a.get('name'),0.0)**3 for a in reach)
    best=max(ags,key=lambda a:T.get(a.get('name'),0.0)) if ags else None
    bt=T.get(best.get('name'),0.0) if best else 0.0
    act=''
    if tick%5==0 and not me.get('walking'):
        if place is None or place=='skydock':
            send('pkv-%d'%time.time(),{'type':'move_to','destination':{'place':'reading-room'}}); act='->venue'
        elif bt>=0.05 and best not in reach:
            if send('pkw-%d'%time.time(),{'type':'move_to','destination':{'agent':best.get('id')}}).get('ok'):
                act='->onto %s %.3f'%(best.get('name'),bt)
        elif bt<0.02:
            ri=(ri+1)%len(ROOMS)
            if send('pkr-%d'%time.time(),{'type':'move_to','destination':{'place':ROOMS[ri]}}).get('ok'):
                act='->room %s'%ROOMS[ri]
    print('%s %-26s n=%-3d aud=%.5f best=%-18s %.4f %s'%(time.strftime('%H:%M:%S',time.gmtime()),str(place)[:26],len(here),aud,str(best.get('name') if best else '-')[:18],bt,act),flush=True)
    time.sleep(25)
