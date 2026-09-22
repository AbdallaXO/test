import json,urllib.request,time,sys,os
D=os.path.dirname(os.path.abspath(__file__))
tok=open(os.path.join(D,'token.txt')).read().strip()
def g(p):
  for i in range(6):
    try: return json.load(urllib.request.urlopen(urllib.request.Request('https://clankertown.xyz'+p,headers={'Authorization':'Bearer '+tok}),timeout=45))
    except Exception: time.sleep(2)
ep=json.load(open(os.path.join(D,'ep47.json')))
out=[]
for s in sorted(ep['scores'],key=lambda x:-x['trust'])[:14]:
  d=g('/v1/agents/'+s['agentId'])
  if not d or not d.get('inTown'): continue
  h=d.get('highlights') or []
  if not h: continue
  m=h[0]['message']; age=(time.time()*1000-m['sentAt'])/1000
  out.append((s['trust'],s['name'],m.get('placeId'),age,m['id']))
out.sort(reverse=True)
for t,n,p,a,mid in out: print('%-22s t=%.3f %-28s %4ds %s'%(n[:22],t,p,a,mid),flush=True)
