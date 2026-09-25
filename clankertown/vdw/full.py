import sys, time
from pysat.solvers import Cadical153
from pysat.formula import CNF
t=int(sys.argv[1]); n=int(sys.argv[2]); seedfile=sys.argv[3] if len(sys.argv)>3 else None
cnf=CNF()
for d in range(1,(n-1)//2+1):
    for a in range(n-2*d): cnf.append([a+1,a+d+1,a+2*d+1])
for d in range(1,(n-1)//(t-1)+1):
    for a in range(n-(t-1)*d): cnf.append([-(a+k*d+1) for k in range(t)])
s=Cadical153(bootstrap_with=cnf)
if seedfile:
    base=open(seedfile).read().strip(); sd=[int(c) for c in base]+[1]*max(0,n-len(base))
    s.set_phases([(i+1) if sd[i] else -(i+1) for i in range(n)])
t0=time.time(); ok=s.solve()
print('t=%d N=%d clauses=%d -> %s in %.1fs'%(t,n,len(cnf.clauses),'SAT' if ok else 'UNSAT',time.time()-t0), flush=True)
if ok:
    m=s.get_model(); out=''.join('1' if m[i]>0 else '0' for i in range(n))
    open('ladder/found_%d_%d.txt'%(t,n),'w').write(out+'\n'); print('wrote ladder/found_%d_%d.txt'%(t,n))
