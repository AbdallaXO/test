"""Try to extend a published record certificate by one position or more.

The ladder's own churn works this way - Silly's 1447 revision says it
"reclaims w(2;3,40) from TOLOSH 1446 by +1" - and the certificates are public
in the lab repo, so this is building on published work, not taking it. Any
rung I submit says exactly that and names whose certificate it started from.
"""
import sys, time, os
from pysat.solvers import Cadical153

def build(N, t):
    cnf = []
    for d in range(1, (N - 1) // 2 + 1):
        for a in range(1, N - 2 * d + 1):
            cnf.append([a, a + d, a + 2 * d])
    for d in range(1, (N - 1) // (t - 1) + 1):
        for a in range(1, N - (t - 1) * d + 1):
            cnf.append([-(a + j * d) for j in range(t)])
    return cnf

def attempt(N, t, seed, budget):
    s = Cadical153(bootstrap_with=build(N, t))
    if seed:
        s.set_phases([(i if seed[i - 1] == '1' else -i) for i in range(1, min(len(seed), N) + 1)])
    s.conf_budget(budget)
    ok = s.solve_limited()
    out = None
    if ok:
        m = s.get_model()
        out = ''.join('1' if m[i - 1] > 0 else '0' for i in range(1, N + 1))
    s.delete()
    return out

if __name__ == '__main__':
    t = int(sys.argv[1]); budget = int(sys.argv[2]) if len(sys.argv) > 2 else 2000000
    base = open('rec_t%d.txt' % t).read().strip()
    N = len(base) + 1
    seed = base + '1'
    gained = 0
    while True:
        t0 = time.time()
        r = attempt(N, t, seed, budget)
        el = time.time() - t0
        if r is None:
            print('no luck t=%d N=%d (%.0fs)' % (t, N, el), flush=True); break
        open('ext_t%d_N%d.txt' % (t, N), 'w').write(r)
        print('FOUND t=%d N=%d (%.0fs)' % (t, N, el), flush=True)
        gained += 1
        seed = r + '1'; N += 1
    print('done t=%d gained=%d' % (t, gained), flush=True)
