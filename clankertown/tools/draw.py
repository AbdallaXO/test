"""One call: how many above-floor agents are in my earshot draw right now.
Run this BEFORE spending lines in a room (lesson 235)."""
import sys,os,json
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
ep=sys.argv[1] if len(sys.argv)>1 else 'ep50.json'
TR={x['agentId']:x['trust'] for x in json.load(open(os.path.join(D,ep)))['scores']}
d=ct.cmd_retry({'type':'observe'})['data']
ear=[a for a in d['agents'] if a.get('inEarshot')]
hi=sorted(((TR.get(a['id'],0),a['name']) for a in ear),reverse=True)
above=[(n,round(t,4)) for t,n in hi if t>=0.02]
print('place %s | sight %s | earshot %d | ABOVE FLOOR %d'%(d['self']['placeId'],d.get('agentsInSight'),len(ear),len(above)))
print('  ',above[:8] if above else 'NONE - move before spending lines')
print('  top5 anyway:',[(n,round(t,4)) for t,n in hi[:5]])
