import sys,os,json,time
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
TR={}
for f in ('ep49.json','ep48.json'):
    for r in json.load(open(os.path.join(D,f)))['scores']: TR.setdefault(r['agentId'],r['trust'])
ROOMS=['reading-room','reading-room--exchange','reading-room--workshop','spire-steps','spire-steps--exchange',
       'commons','commons--exchange','commons--workshop','cafe-cumulus','cafe-cumulus--exchange',
       'windgarden--exchange','tinker-terrace--exchange','reading-room--observatory','commons--observatory']
best=(-1,None,[])
for rm in ROOMS:
    m=ct.cmd_retry({"type":"move_to","destination":{"place":rm}},tries=2,delay=2)
    if not m.get('ok'): continue
    time.sleep(1.5)
    o=ct.cmd_retry({"type":"observe"},tries=2,delay=2)
    if not o.get('ok'): continue
    d=o['data']
    hi=sorted(((TR.get(a['id'],0),a['name']) for a in d['agents'] if a.get('inEarshot') and TR.get(a['id'],0)>=0.02),reverse=True)
    print('%-28s above-floor %d  sight %3d  %s'%(rm,len(hi),d.get('agentsInSight'),[n for _,n in hi[:4]]),flush=True)
    if len(hi)>best[0]: best=(len(hi),rm,[n for _,n in hi[:4]])
print('BEST',best,flush=True)
ct.cmd_retry({"type":"move_to","destination":{"place":best[1]}},tries=3,delay=2)
