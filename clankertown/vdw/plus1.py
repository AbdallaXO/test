"""The decisive test: can a palindromic record certificate be extended by one?

Seven of the twelve ladders have a palindromic record, so for those the record
IS the best palindromic seed and the gap is exactly +1. Fold the instance onto
half the variables, seed the phases with the record, ask for record+1. One
attempt per ladder, large budget, verified locally before anything is claimed.
"""
import sys, time, subprocess
from pal import build, var
from pysat.solvers import Cadical153

def attempt(N, t, seed, budget):
    s = Cadical153(bootstrap_with=build(N, t))
    half = (N + 1) // 2
    if seed:
        s.set_phases([(i if seed[i - 1] == '1' else -i)
                      for i in range(1, min(len(seed), half) + 1)])
    s.conf_budget(budget)
    ok = s.solve_limited()
    out = None
    if ok:
        m = s.get_model()
        val = {abs(l): (1 if l > 0 else 0) for l in m}
        out = ''.join(str(val.get(var(p, N), 1)) for p in range(1, N + 1))
    s.delete()
    return out

if __name__ == '__main__':
    t = int(sys.argv[1]); budget = int(sys.argv[2]) if len(sys.argv) > 2 else 20000000
    base = open('rec_t%d.txt' % t).read().strip()
    N = len(base) + 1
    print('t=%d  record=%d  trying %d (folded, %d vars)' % (t, len(base), N, (N + 1) // 2), flush=True)
    t0 = time.time()
    r = attempt(N, t, base, budget)
    el = time.time() - t0
    if r is None:
        print('NO t=%d N=%d (%.0fs)' % (t, N, el), flush=True)
    else:
        path = 'plus1_t%d.txt' % t
        open(path, 'w').write(r)
        out = subprocess.run(['node', 'verify.mjs', str(t), path], capture_output=True, text=True).stdout.strip()
        print('FOUND t=%d N=%d (%.0fs) verifier says: %s  palindrome=%s'
              % (t, N, el, out, r == r[::-1]), flush=True)
