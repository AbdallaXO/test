"""Exact repair of a w(2;3,t) record certificate extended by one position.

The seed is a valid colouring of length N-1, so the extended string is one or
two violations away from valid -- WalkSAT at noise 0.15 throws that away and
wanders to 400+ violations, which is what my first three runs did. This instead
searches exactly and locally: every violated constraint names its own positions,
and a repair must flip one of them.
"""
import sys

def violations(s, t):
    n = len(s)
    zs = {i for i, c in enumerate(s) if c == 0}
    zl = sorted(zs)
    bad3 = []
    for ai, a in enumerate(zl):
        for b in zl[ai + 1:]:
            c = 2 * b - a
            if c < n and c in zs:
                bad3.append((a, b, c))
    badt = []
    for d in range(1, (n - 1) // (t - 1) + 1):
        for a in range(n):
            if s[a] != 1 or (a - d >= 0 and s[a - d] == 1):
                continue
            run = 0
            j = a
            while j < n and s[j] == 1:
                run += 1
                j += d
            if run >= t:
                for off in range(run - t + 1):
                    badt.append(tuple(a + (off + k) * d for k in range(t)))
    return bad3, badt

def nviol(s, t):
    b3, bt = violations(s, t)
    return len(b3) + len(bt)

def solve(base, t):
    s = [int(c) for c in base]
    b3, bt = violations(s, t)
    cands = set()
    for ap in b3 + bt:
        cands.update(ap)
    print('  start: %d violations (%d 3-APs, %d %d-APs), %d candidate positions'
          % (len(b3) + len(bt), len(b3), len(bt), t, len(cands)), flush=True)
    for i in sorted(cands):
        s[i] ^= 1
        if nviol(s, t) == 0:
            print('  SOLVED by flipping %d' % i, flush=True)
            return ''.join(map(str, s))
        s[i] ^= 1
    print('  no single flip works; trying pairs', flush=True)
    best = (len(b3) + len(bt), None)
    for i in sorted(cands):
        s[i] ^= 1
        nb3, nbt = violations(s, t)
        if len(nb3) + len(nbt) < best[0]:
            best = (len(nb3) + len(nbt), (i,))
        c2 = set()
        for ap in nb3 + nbt:
            c2.update(ap)
        for j in sorted(c2):
            if j == i:
                continue
            s[j] ^= 1
            if nviol(s, t) == 0:
                print('  SOLVED by flipping %d and %d' % (i, j), flush=True)
                return ''.join(map(str, s))
            s[j] ^= 1
        s[i] ^= 1
    print('  no pair works; best single-flip residue %s' % (best,), flush=True)
    return None

if __name__ == '__main__':
    t = int(sys.argv[1]); seed = sys.argv[2]
    tail = sys.argv[3] if len(sys.argv) > 3 else '1'
    base = open(seed).read().strip() + tail
    print('t=%d N=%d tail=%r' % (t, len(base), tail), flush=True)
    r = solve(base, t)
    if r:
        out = 'ladder/found_%d_%d.txt' % (t, len(r))
        open(out, 'w').write(r + '\n')
        print('  wrote ' + out, flush=True)
