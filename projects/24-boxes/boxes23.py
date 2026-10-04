"""Dots and Boxes on R x C boxes, solved exactly by the same rule as boxes.py (cycle 198). Lines: horizontals
H(r,c) r=0..R c=0..C-1, then verticals V(r,c) r=0..R-1 c=0..C. value(mask) = best final margin for the mover."""
import sys
from functools import lru_cache
sys.setrecursionlimit(100000)
def solve(R, C):
    nH = (R + 1) * C
    H = lambda r, c: r * C + c
    V = lambda r, c: nH + r * (C + 1) + c
    L = nH + R * (C + 1)
    boxes = [(H(i, j), H(i + 1, j), V(i, j), V(i, j + 1)) for i in range(R) for j in range(C)]
    touch = [[b for b in boxes if e in b] for e in range(L)]
    full = (1 << L) - 1
    @lru_cache(None)
    def value(m):
        if m == full: return 0
        best = -99
        for e in range(L):
            if m >> e & 1: continue
            k = sum(1 for b in touch[e] if all(m >> x & 1 for x in b if x != e)); t = m | 1 << e
            v = k + value(t) if k else -value(t)
            if v > best: best = v
        return best
    v0 = value(0); n = value.cache_info().currsize; value.cache_clear()
    return v0, n, L
for R, C in ((1, 1), (1, 2), (1, 3), (2, 2), (2, 3)):
    v0, n, L = solve(R, C)
    print(f"{R}x{C} boxes ({L} lines): first player's margin {v0:+d} ({'first wins' if v0 > 0 else 'second wins' if v0 < 0 else 'draw'}); positions {n}")
