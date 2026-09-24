"""Try quasicrystal (Sturmian) zero-sets, which the counting argument points at.

The obstruction for w(2;3,t) is that the ~N/t zeros must be near-perfectly
equidistributed across every modulus up to N/t at once while staying 3-AP-free.
A set {n : frac(n*theta + phi) < gamma} with theta irrational is exactly the
maximally equidistributed object of its density, so it is the natural candidate
that pure local search will never stumble onto.
"""
import sys

def zeros_mask(N, theta, phi, gamma):
    s = bytearray(b'1') * N
    for n in range(1, N + 1):
        if ((n * theta + phi) % 1.0) < gamma:
            s[n - 1] = 48  # '0'
    return s

def ok(s, t):
    n = len(s)
    for a in range(n):
        c = s[a]; k = 3 if c == 48 else t
        d = 1
        while a + (k - 1) * d < n:
            j = 1
            while j < k and s[a + j * d] == c: j += 1
            if j == k: return False
            d += 1
    return True

def best_N(theta, phi, gamma, t, lo, hi):
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if ok(zeros_mask(mid, theta, phi, gamma), t):
            best = mid; lo = mid + 1
        else:
            hi = mid - 1
    return best

if __name__ == '__main__':
    t = int(sys.argv[1]); hi = int(sys.argv[2])
    import math
    cands = []
    golden = (math.sqrt(5) - 1) / 2
    for theta in (golden, math.sqrt(2) % 1, math.sqrt(3) % 1, math.pi % 1, math.e % 1,
                  1 / math.sqrt(2), golden ** 2, (math.sqrt(5) + 1) / 2 % 1):
        for gamma in (1.0 / (t - 1), 1.0 / (t - 2), 1.0 / (t - 3), 1.0 / (t - 5), 1.0 / (t + 1)):
            for phi in (0.0, 0.1, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9):
                b = best_N(theta, phi, gamma, t, 50, hi)
                cands.append((b, theta, phi, gamma))
    cands.sort(reverse=True)
    for b, th, ph, ga in cands[:6]:
        print('N=%d theta=%.9f phi=%.2f gamma=%.6f' % (b, th, ph, ga), flush=True)
    b, th, ph, ga = cands[0]
    open('sturm_t%d_best.txt' % t, 'w').write(zeros_mask(b, th, ph, ga).decode())
