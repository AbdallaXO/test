"""Walk N upward, seeding each solve with the previous solution's phases.

A cold solve at the record boundary sits right on the satisfiability threshold
and Cadical can grind on it for hours. Starting well below the record, where
the instance is easy, and stepping up while re-using the previous assignment as
phase hints gives the solver a nearly-satisfying start every time. This is how
the published bounds were found, not by cold-starting the hard instance.
"""
import sys, os, time
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

def solve(N, t, seed=None, budget=None):
    s = Cadical153(bootstrap_with=build(N, t))
    if seed:
        s.set_phases([(i if seed[i - 1] == '1' else -i) for i in range(1, min(len(seed), N) + 1)])
    ok = s.solve() if budget is None else s.solve_limited(expect_interrupt=False)
    if not ok:
        s.delete(); return None
    m = s.get_model()
    out = ''.join('1' if m[i - 1] > 0 else '0' for i in range(1, N + 1))
    s.delete(); return out

if __name__ == '__main__':
    t = int(sys.argv[1]); start = int(sys.argv[2]); target = int(sys.argv[3])
    step = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    seed = None; N = start; best = None
    while N <= target:
        t0 = time.time()
        r = solve(N, t, seed)
        el = time.time() - t0
        if r is None:
            print('UNSAT t=%d N=%d (%.0fs)' % (t, N, el), flush=True); break
        best = r; seed = r + '1' * step
        open('walk_t%d_best.txt' % t, 'w').write(r)
        print('SAT t=%d N=%d (%.0fs)' % (t, N, el), flush=True)
        N += step
    if best:
        print('BEST t=%d N=%d -> walk_t%d_best.txt' % (t, len(best), t), flush=True)
