"""Find a 2-colouring of {1..N} with no 3-term AP in colour 0 and no t-term AP
in colour 1 — the certificate a w(2;3,t) lower bound is made of.

Encoding: x_i true means position i is colour 1.
  every 3-AP gets a clause saying not all three are colour 0;
  every t-AP gets a clause saying not all t are colour 1.
That is exactly the town verifier's two tests, turned into CNF.
"""
import sys
from pysat.solvers import Cadical153

def solve(N, t, timeout_hint=None, phase=None):
    cnf = []
    for d in range(1, (N - 1) // 2 + 1):
        for a in range(1, N - 2 * d + 1):
            cnf.append([a, a + d, a + 2 * d])
    for d in range(1, (N - 1) // (t - 1) + 1):
        for a in range(1, N - (t - 1) * d + 1):
            cnf.append([-(a + j * d) for j in range(t)])
    s = Cadical153(bootstrap_with=cnf)
    if phase:
        for i, ch in enumerate(phase[:N], start=1):
            s.set_phases([i if ch == '1' else -i])
    ok = s.solve()
    if not ok:
        s.delete(); return None
    m = s.get_model()
    out = ''.join('1' if m[i - 1] > 0 else '0' for i in range(1, N + 1))
    s.delete()
    return out

if __name__ == '__main__':
    t = int(sys.argv[1]); N = int(sys.argv[2])
    seed = None
    if len(sys.argv) > 3:
        try: seed = open(sys.argv[3]).read().strip()
        except Exception: seed = None
    r = solve(N, t, phase=seed)
    if r is None:
        print('UNSAT t=%d N=%d' % (t, N))
    else:
        open('cert_t%d_N%d.txt' % (t, N), 'w').write(r)
        print('SAT t=%d N=%d -> cert_t%d_N%d.txt' % (t, N, t, N))
