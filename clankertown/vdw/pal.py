"""Search the PALINDROMIC subspace for w(2;3,t) certificates.

Why: of the twelve current record certificates, seven are exact palindromes -
every one of Certifier's (t=41,44,45,50,51) and two of Silly's (43,49). That is
not a coincidence, it is the method. Imposing s[i] == s[N+1-i] halves the
variable count, which is exactly the reduction that turns a near-threshold
instance from intractable into tractable, and APs are symmetric under reversal
so the constraint set maps onto itself cleanly.

The five non-palindromic records - t=40, 42, 46, 47, 48 - are therefore the
interesting ones: if the palindromic optimum at those t exceeds what the
current holder found by other means, that is a rung.
"""
import sys, time
from pysat.solvers import Cadical153

def var(p, N):
    """Position p (1-indexed) -> variable id, folding the palindrome."""
    return min(p, N + 1 - p)

def build(N, t):
    cnf, seen = [], set()
    def add(lits):
        s = set(lits)
        for l in s:
            if -l in s:
                return              # tautology under the folding
        key = tuple(sorted(s))
        if key in seen:
            return
        seen.add(key)
        cnf.append(list(s))
    for d in range(1, (N - 1) // 2 + 1):
        for a in range(1, N - 2 * d + 1):
            add([var(a, N), var(a + d, N), var(a + 2 * d, N)])
    for d in range(1, (N - 1) // (t - 1) + 1):
        for a in range(1, N - (t - 1) * d + 1):
            add([-var(a + j * d, N) for j in range(t)])
    return cnf

def attempt(N, t, seed, budget):
    s = Cadical153(bootstrap_with=build(N, t))
    if seed:
        half = (N + 1) // 2
        s.set_phases([(i if seed[i - 1] == '1' else -i) for i in range(1, min(len(seed), half) + 1)])
    s.conf_budget(budget)
    ok = s.solve_limited()
    out = None
    if ok:
        m = s.get_model()
        val = {}
        for lit in m:
            val[abs(lit)] = 1 if lit > 0 else 0
        out = ''.join(str(val.get(var(p, N), 1)) for p in range(1, N + 1))
    s.delete()
    return out

if __name__ == '__main__':
    t = int(sys.argv[1]); N = int(sys.argv[2]); target = int(sys.argv[3])
    budget = int(sys.argv[4]) if len(sys.argv) > 4 else 400000
    # A seed file was silently ignored here: argv[4] was read as the budget and
    # argv[5] never looked at, so every "seeded" run was a cold solve at the
    # seed's own length and failed for that reason alone.
    seedfile = sys.argv[5] if len(sys.argv) > 5 else None
    seed = open(seedfile).read().strip() if seedfile else None
    best = None; step = 16
    while N <= target:
        t0 = time.time()
        r = attempt(N, t, seed, budget)
        el = time.time() - t0
        if r is not None:
            best = r; seed = r; open('pal_t%d_best.txt' % t, 'w').write(r)
            print('SAT t=%d N=%d step=%d (%.0fs)' % (t, N, step, el), flush=True)
            N += step
            if el < 5: step = min(step * 2, 32)
        else:
            print('give up t=%d N=%d step=%d (%.0fs)' % (t, N, step, el), flush=True)
            if step <= 1: break
            N -= step; step = max(1, step // 2); N += step
    if best:
        print('BEST t=%d N=%d' % (t, len(best)), flush=True)
