"""Cycle 56: is the 36-cell E-speed object part of the E^n family (same speed, width grows with n)?
Martinez's catalogue: E, E-bar and E^n all move at -4/15; E^n "widens with n". My object has a repeating middle.
Prediction (written first): cutting out, or duplicating, one 14-cell stretch of that repeating middle (the raw row,
so the ether stays aligned) gives another exact glider with period 30, shift -8, and widths step by a fixed amount.
Control: the same surgery on a LONE E (no repeating middle) should NOT give a clean glider at every cut point."""
import numpy as np
TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
step = lambda r: TABLE[4 * np.roll(r, 1) + 2 * r + np.roll(r, -1)]
NT = 60; W = 14 * NT; base = np.tile(TILE, NT); L0 = 14 * 30
SHIFT = next(d for d in range(W) if np.array_equal(np.roll(base, d), step(base)))

def evolve(row, clean, T):
    for _ in range(T): row, clean = step(row), step(clean)
    return row, clean
def make(sep, delay, T=3600):                                    # the E+G collision from cycle 54
    row, clean = base.copy(), base.copy(); row[L0 + 6] ^= 1
    for t in range(T):
        if t == delay:
            for o in (2, 18): row[(L0 + 14 * sep + o + SHIFT * t) % W] ^= 1
        row, clean = step(row), step(clean)
    return row, clean
def lone_e(T=900):
    row = base.copy(); row[L0 + 6] ^= 1; return evolve(row, base.copy(), T)
def glider(row, clean, pmax=60):
    """(p, d, cells, span) if the whole defect is exactly periodic for 3 periods, else None."""
    n = len(row); hist = []
    for _ in range(3 * pmax + 1): hist.append(row != clean); row, clean = step(row), step(clean)
    x = np.nonzero(hist[0])[0]
    if x.size == 0: return None
    xs = np.sort(x); gaps = np.diff(np.r_[xs, xs[0] + n]); spanw = n - gaps.max()
    for p in range(1, pmax + 1):
        for d in range(-20, 21):
            if all(np.array_equal(np.roll(hist[r * p], d), hist[(r + 1) * p]) for r in range(3)): return p, d, int(x.size), int(spanw)
    return None
def surgery(row, clean, m, k):
    """k>0: duplicate k x 14 cells starting at m; k<0: remove |k| x 14 cells at m. Same edit to the clean ether."""
    if k > 0: f = lambda a: np.r_[a[:m], np.tile(a[m:m + 14], k), a[m:]]
    else: f = lambda a: np.r_[a[:m], a[m - 14 * k:]]
    return f(row), f(clean)

obj = make(4, 4)
x = np.nonzero(obj[0] != obj[1])[0]; a, b = int(x.min()), int(x.max())
print("object:", glider(*obj), "occupies", a, "..", b)
print("raw row over the object:", "".join(map(str, obj[0][a:b + 1])))
for name, (row, clean), (lo, hi) in [("OBJECT", obj, (a, b)), ("LONE E (control)", lone_e(), (None, None))]:
    if hi is None:
        y = np.nonzero(row != clean)[0]; lo, hi = int(y.min()), int(y.max())
    print(f"\n{name}: surgery at every cut point m in its body")
    tally = {}
    for k in (-2, -1, 1, 2, 3):
        res = []
        for m in range(lo + 1, hi - 14 * max(0, -k)):
            g = glider(*surgery(row, clean, m, k))
            res.append(g)
            key = (k, g[:2] if g else None); tally[key] = tally.get(key, 0) + 1
        ok = [r for r in res if r and r[:2] == (30, -8)]
        print(f"  k={k:+d} x14 cells: {len(ok)}/{len(res)} cut points give an exact (30,-8) glider;"
              f" sizes {sorted({(r[2], r[3]) for r in ok})}")
