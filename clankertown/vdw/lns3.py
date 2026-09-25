"""Large-neighbourhood search for w(2;3,t) record+1, seeded from the town record.

Why this and not the WalkSAT I ran first: the extended record is ONE violation
away from valid, and noise-0.15 WalkSAT walks away from it -- measured, it went
from 1 violation to 514 in eight million flips. And exact repair by flipping one
or two positions fails, so the fix is not local to the broken progression: the
record is tight and needs a rearrangement.

So: build the CNF once, then hand a SAT solver the whole problem with every
variable OUTSIDE a window fixed to the seed's value as assumptions. The solver
decides the window exactly. A window that fails is proof that this stretch alone
cannot absorb the extra position; slide and widen.

usage: python3 lns3.py <t> <N> <seedfile> [windows] [seed]
"""
import sys, random, time, os
from pysat.solvers import Cadical153
from pysat.formula import CNF

def build(n, t):
    cnf = CNF()
    for d in range(1, (n - 1) // 2 + 1):          # no 3-AP all in colour 0
        for a in range(n - 2 * d):
            cnf.append([a + 1, a + d + 1, a + 2 * d + 1])
    for d in range(1, (n - 1) // (t - 1) + 1):    # no t-AP all in colour 1
        for a in range(n - (t - 1) * d):
            cnf.append([-(a + k * d + 1) for k in range(t)])
    return cnf

def main():
    t = int(sys.argv[1]); n = int(sys.argv[2]); seedfile = sys.argv[3]
    budget = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    rng = random.Random(int(sys.argv[5]) if len(sys.argv) > 5 else 1)
    base = open(seedfile).read().strip()
    seed = [int(c) for c in base]
    while len(seed) < n:
        seed.append(1)
    seed = seed[:n]

    t0 = time.time()
    cnf = build(n, t)
    print('t=%d N=%d clauses=%d built in %.1fs' % (t, n, len(cnf.clauses), time.time() - t0), flush=True)
    s = Cadical153(bootstrap_with=cnf)

    # A free run first: the whole problem, seed only as a hint via phases.
    s.set_phases([(i + 1) if seed[i] else -(i + 1) for i in range(n)])

    width = 200
    tried = 0
    while tried < budget:
        lo = rng.randrange(0, n)
        hi = min(n, lo + width)
        assume = [(i + 1) if seed[i] else -(i + 1) for i in range(n) if not (lo <= i < hi)]
        ok = s.solve(assumptions=assume)
        tried += 1
        if ok:
            m = s.get_model()
            out = ''.join('1' if m[i] > 0 else '0' for i in range(n))
            path = 'ladder/found_%d_%d.txt' % (t, n)
            open(path, 'w').write(out + '\n')
            print('SOLVED t=%d N=%d window=[%d,%d) width=%d after %d windows, %.1fs -> %s'
                  % (t, n, lo, hi, width, tried, time.time() - t0, path), flush=True)
            return 0
        if tried % 25 == 0:
            width = min(int(width * 1.35) + 40, n)
            print('  %d windows, none feasible; widening to %d (%.0fs)' % (tried, width, time.time() - t0), flush=True)
    print('FAILED t=%d N=%d after %d windows' % (t, n, tried), flush=True)
    return 1

sys.exit(main())
