"""LNS again, but building the CNF once and pinning positions with assumptions.

The first version rebuilt a 500k-1.2M clause formula for every window it tried,
so almost all the time went into Python list-building rather than search. One
solver, held open, with the pinned positions passed as assumptions: the clause
database and everything Cadical learns are reused across hundreds of windows.
"""
import sys, time, random
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

def main(t, budget, seconds):
    base = open('rec_t%d.txt' % t).read().strip()
    start = len(base)
    deadline = time.time() + seconds
    rnd = random.Random(t * 7919 + 13)
    gained = 0
    while time.time() < deadline:
        N = len(base) + 1
        s = Cadical153(bootstrap_with=build(N, t))
        found = None
        plans = [('tail', W) for W in (40, 80, 160, 320, 600, 1000, 1500)]
        plans += [('rand', rnd.choice([100, 200, 400, 800])) for _ in range(120)]
        for kind, W in plans:
            if time.time() > deadline: break
            if kind == 'tail':
                lo, hi = max(1, N - W), N
            else:
                lo = rnd.randint(1, max(1, N - W)); hi = min(N - 1, lo + W)
            assumptions = [(i if base[i - 1] == '1' else -i)
                           for i in range(1, min(len(base), N) + 1)
                           if not (lo <= i <= hi)]
            s.conf_budget(budget)
            if s.solve_limited(assumptions=assumptions):
                m = s.get_model()
                found = ''.join('1' if m[i - 1] > 0 else '0' for i in range(1, N + 1))
                print('EXTEND t=%d -> %d via %s %d..%d' % (t, N, kind, lo, hi), flush=True)
                break
        s.delete()
        if not found:
            print('stuck t=%d at %d (started %d)' % (t, len(base), start), flush=True)
            break
        base = found
        open('lns_t%d_best.txt' % t, 'w').write(base)
        gained += 1
    print('done t=%d gained=%d final=%d' % (t, gained, len(base)), flush=True)

if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 60000,
         int(sys.argv[3]) if len(sys.argv) > 3 else 7000)
