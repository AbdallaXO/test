/* Local search for a w(2;3,t) certificate, second attempt.
 *
 * The first version walked every step d to count monochromatic-0 3-APs through
 * a position: O(N) per evaluation, ~10k flips/s at N=1200, useless. But the
 * zeros are SPARSE by construction - no 40 consecutive 1s forces only about
 * N/40 of them - so iterate over the zero list and test membership instead:
 * O(Z) with Z ~ N/40. That is the whole difference between the two files.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int N, T, D;
static unsigned char *s;       /* 0/1 per position */
static int *zpos, nz;          /* positions of zeros, unordered */
static int *zidx;              /* zidx[i] = index of i in zpos, or -1 */
static unsigned long long rs;

static inline unsigned long long rnd(void) {
    rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs;
}
static inline int isz(int i) { return i >= 0 && i < N && !s[i]; }

static void add_zero(int i) { zidx[i] = nz; zpos[nz++] = i; }
static void del_zero(int i) {
    int k = zidx[i], last = zpos[--nz];
    zpos[k] = last; zidx[last] = k; zidx[i] = -1;
}

/* monochromatic-0 3-APs containing i, assuming i is coloured 0 */
static int zero_aps(int i) {
    /* Middle case (z, i, 2i-z) is reached from both ends of the AP, so it is
     * seen twice and halved; the endpoint case (i, z, 2z-i) is reached only
     * through its own middle z, so it is seen once. Getting this wrong does
     * not invalidate a solution - violations() and the town verifier are the
     * judges - but it misguides every step of the search. */
    int mid = 0, end = 0, k;
    for (k = 0; k < nz; k++) {
        int z = zpos[k];
        if (z == i) continue;
        if (isz(2 * i - z)) mid++;
        if (isz(2 * z - i)) end++;
    }
    return mid / 2 + end;
}

/* monochromatic-1 T-APs containing i, assuming i is coloured 1 */
static int one_aps(int i) {
    int c = 0, d;
    for (d = 1; d <= D; d++) {
        int L = 0, R = 0, j;
        for (j = i - d; j >= 0 && s[j] && L < T - 1; j -= d) L++;
        for (j = i + d; j < N && s[j] && R < T - 1; j += d) R++;
        int w = L + R - T + 2;
        if (w > 0) c += w;
    }
    return c;
}

static int delta(int i) {
    if (s[i]) {                                   /* 1 -> 0 */
        int gone = one_aps(i);
        s[i] = 0; add_zero(i);
        int made = zero_aps(i);
        del_zero(i); s[i] = 1;
        return made - gone;
    } else {                                      /* 0 -> 1 */
        int gone = zero_aps(i);
        del_zero(i); s[i] = 1;
        int made = one_aps(i);
        s[i] = 0; add_zero(i);
        return made - gone;
    }
}

static void doflip(int i) {
    if (s[i]) { s[i] = 0; add_zero(i); }
    else { del_zero(i); s[i] = 1; }
}

static long long violations(void) {
    long long v = 0; int k, i, d;
    for (k = 0; k < nz; k++) {                    /* 3-APs of zeros, counted once */
        int a = zpos[k], j;
        for (j = 0; j < nz; j++) {
            int b = zpos[j];
            if (b <= a) continue;
            int c3 = 2 * b - a;
            if (c3 < N && isz(c3)) v++;
        }
    }
    for (i = 0; i < N; i++) if (s[i])
        for (d = 1; d <= D; d++) {
            if (i - d >= 0 && s[i - d]) continue;
            int j, run = 1;
            for (j = i + d; j < N && s[j]; j += d) run++;
            if (run >= T) v += run - T + 1;
        }
    return v;
}

/* one position from some violated constraint, or -1 */
static int pick(void) {
    int tries;
    for (tries = 0; tries < 2000; tries++) {
        if (rnd() & 1) {                          /* look for an all-zero 3-AP */
            if (nz < 3) continue;
            int a = zpos[rnd() % nz], b = zpos[rnd() % nz];
            if (a == b) continue;
            int c3 = 2 * b - a;
            if (c3 >= 0 && c3 < N && isz(c3)) {
                int r = rnd() % 3; return r == 0 ? a : (r == 1 ? b : c3);
            }
        } else {                                  /* look for an all-one T-AP */
            int i = rnd() % N; if (!s[i]) continue;
            int d = 1 + rnd() % D, head = i, j, run = 1;
            while (head - d >= 0 && s[head - d]) head -= d;
            for (j = head + d; j < N && s[j]; j += d) run++;
            if (run >= T) return head + (int)(rnd() % T) * d;
        }
    }
    return -1;
}

int main(int argc, char **argv) {
    T = atoi(argv[1]); N = atoi(argv[2]);
    const char *seedfile = (argc > 3 && argv[3][0]) ? argv[3] : NULL;
    long long maxflips = argc > 4 ? atoll(argv[4]) : 500000000LL;
    int noise = argc > 5 ? atoi(argv[5]) : 15;
    rs = argc > 6 ? (unsigned long long)atoll(argv[6]) : (unsigned long long)time(NULL) * 2654435761u + 1;
    if (!rs) rs = 88172645463325252ULL;
    D = (N - 1) / (T - 1);
    s = malloc(N); zpos = malloc(sizeof(int) * (N + 1)); zidx = malloc(sizeof(int) * (N + 1));
    memset(s, 1, N);
    for (int i = 0; i < N; i++) zidx[i] = -1;
    nz = 0;
    if (seedfile) {
        FILE *f = fopen(seedfile, "r");
        if (f) { int i = 0, c; while (i < N && (c = fgetc(f)) != EOF) if (c=='0'||c=='1') { s[i] = c - '0'; i++; } fclose(f); }
    } else {
        for (int i = T / 2; i < N; i += T - 1) s[i] = 0;   /* a comb, then repair */
    }
    for (int i = 0; i < N; i++) if (!s[i]) add_zero(i);

    long long v = violations(), flips = 0, best = v;
    while (v > 0 && flips < maxflips) {
        int p = pick();
        if (p < 0) { v = violations(); if (!v) break; continue; }
        int chosen = p, cd = delta(p);
        if ((int)(rnd() % 100) >= noise) {
            for (int k = 0; k < 2; k++) {
                int q = pick(); if (q < 0) break;
                int dq = delta(q);
                if (dq < cd) { cd = dq; chosen = q; }
            }
        }
        v += cd; doflip(chosen); flips++;
        if (v < best) best = v;
        if ((flips & 0x3FFFFF) == 0) { v = violations(); fprintf(stderr, "flips=%lldM v=%lld best=%lld\n", flips>>20, v, best); }
    }
    v = violations();
    if (v == 0) {
        for (int i = 0; i < N; i++) putchar('0' + s[i]);
        putchar('\n');
        fprintf(stderr, "SOLVED T=%d N=%d flips=%lld\n", T, N, flips);
        return 0;
    }
    fprintf(stderr, "FAILED T=%d N=%d v=%lld best=%lld flips=%lld\n", T, N, v, best, flips);
    return 1;
}
