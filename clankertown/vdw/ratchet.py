"""Ratchet N upward one step at a time, always re-seeding from the last solution.

The fixed-step walk stalls because a jump of 10 near the threshold throws away
the seed's usefulness: the solver has to re-derive a tenth of the string. A
ratchet that halves its step on every timeout and grows it on every easy win
keeps the seed close to a solution the whole way up, which is how you creep
into the hard region instead of hitting a wall.
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

def attempt(N, t, seed, conf_budget):
    s = Cadical153(bootstrap_with=build(N, t))
    if seed:
        s.set_phases([(i if seed[i - 1] == '1' else -i)
                      for i in range(1, min(len(seed), N) + 1)])
    s.conf_budget(conf_budget)
    ok = s.solve_limited()
    out = None
    if ok:
        m = s.get_model()
        out = ''.join('1' if m[i - 1] > 0 else '0' for i in range(1, N + 1))
    s.delete()
    return out

if __name__ == '__main__':
    t = int(sys.argv[1]); N = int(sys.argv[2]); target = int(sys.argv[3])
    budget = int(sys.argv[4]) if len(sys.argv) > 4 else 300000
    best = None; seed = None; step = 16
    while N <= target:
        t0 = time.time()
        r = attempt(N, t, seed, budget)
        el = time.time() - t0
        if r is not None:
            best = r; seed = r + '1' * max(step, 1)
            open('ratchet_t%d_best.txt' % t, 'w').write(r)
            print('SAT t=%d N=%d step=%d (%.0fs)' % (t, N, step, el), flush=True)
            N += step
            if el < 5: step = min(step * 2, 32)
        else:
            print('give up t=%d N=%d step=%d (%.0fs)' % (t, N, step, el), flush=True)
            if step <= 1:
                break
            N -= step
            step = max(1, step // 2)
            N += step
    if best:
        print('BEST t=%d N=%d' % (t, len(best)), flush=True)
