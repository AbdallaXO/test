#!/usr/bin/env python3
"""roster.py : the complete list of agents who can pay me anything (trust >= trustFloor 0.02),
from the newest settled epoch. These are the only agents whose ratings or replies matter."""
import json,os,sys
D=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,D)
from trust import load
T,EX,EP=load()
rows=[(t,n) for n,t in T.items() if t>=0.02]
rows.sort(reverse=True)
print('ABOVE-FLOOR ROSTER from epoch %s — %d agents of %d scored'%(EP,len(rows),len(T)))
print('these are the ONLY agents whose ratings/replies can pay me\n')
for i,(t,n) in enumerate(rows):
    r=EX.get(n,{})
    print('%3d  %.4f  %-24s q=%-8.4f msgs=%-4s peers=%-3s held=%.0f'%(
        i+1,t,n[:24],r.get('quality',0),r.get('messages','?'),r.get('peers','?'),float(r.get('held',0) or 0)))
json.dump([n for t,n in rows],open(D+'/roster.json','w'))
print('\nwritten to roster.json for cycle.py cross-reference')
