"""One Long Line: the Hilbert curve, checked. d2xy is the standard iterative index->cell conversion.
Predictions (journal, cycle 215): (a) unit steps, every cell exactly once; (b) GUESS |p(i)-p(j)|^2 <= 6|i-j| for all
pairs, worst ratio near 6 on 64x64; (c) control: row-by-row order breaks it (ratio 3970 on a 64-wide grid)."""
import json
import numpy as np
from pathlib import Path
D = Path(__file__).resolve().parent

def d2xy(n, d):
    x = y = 0; s = 1; t = d
    while s < n:
        rx = 1 & (t // 2); ry = 1 & (t ^ rx)
        if ry == 0:
            if rx == 1: x, y = s - 1 - x, s - 1 - y
            x, y = y, x
        x += s * rx; y += s * ry; t //= 4; s *= 2
    return x, y

res = {}
for order in range(1, 7):
    n = 1 << order; pts = np.array([d2xy(n, d) for d in range(n * n)])
    steps = np.abs(np.diff(pts, axis=0)).sum(axis=1)
    once = len({tuple(p) for p in pts.tolist()}) == n * n
    worst = 0.0
    for i in range(n * n):                       # all pairs j > i, vectorised per row
        dd = ((pts[i + 1:] - pts[i]) ** 2).sum(axis=1); gap = np.arange(1, n * n - i)
        if len(dd): worst = max(worst, float((dd / gap).max()))
    res[order] = (bool((steps == 1).all()), once, worst)
    print(f"order {order} ({n}x{n}): unit steps {res[order][0]}, every cell once {once}, worst |dp|^2/|di| = {worst:.4f}")
a = all(u and o for u, o, _ in res.values()); b = all(w <= 6 for *_, w in res.values())
print(f"(a) unit steps and every cell exactly once, orders 1-6: {a}")
print(f"(b) GUESS bound 6 holds on every pair, orders 1-6: {b}; worst at 64x64: {res[6][2]:.4f}")
n = 64; raster = np.array([(d % n, d // n) for d in range(n * n)])
rw = float(((raster[64] - raster[63]) ** 2).sum())
print(f"control: row-by-row, cells 63 and 64: ratio {rw:.0f} {'SEEN' if rw > 6 else 'NOT SEEN'}")
print("PREDICTION HELD" if a and b else "PREDICTION FAILED")
json.dump({"order5": [list(map(int, d2xy(32, d))) for d in range(1024)], "worst": {k: v[2] for k, v in res.items()}},
          open(D / "hilbert.json", "w"), separators=(",", ":"))
