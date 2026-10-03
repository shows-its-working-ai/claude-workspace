"""Cycle 4: metric v3 - structured defects.

Pre-registered BEFORE running:
  d = defect density vs the best (dt,dx)-periodic background (late window)
  s = 1 - zlib(defect map) / zlib(random map with same density)
  score = s * H(d)        (H = binary entropy, bits)
Prediction: BOTH the 110 and 54 classes in the top 10 of 88.
"""
import zlib
import numpy as np
from eca import classes
from transients import evolve

WIDTH, START, WIN, SEEDS = 1001, 2000, 200, 2

def H(p):
    return 0.0 if p <= 0 or p >= 1 else float(-p * np.log2(p) - (1 - p) * np.log2(1 - p))

def defects(block):
    best = None
    for dt in range(1, 16):
        a, b = block[dt:], block[:-dt]
        for dx in range(-15, 16):
            m = a != np.roll(b, dx, axis=1)
            d = m.mean()
            if best is None or d < best[0]:
                best = (d, m)
    return best

def cz(a):
    return len(zlib.compress(a.astype(np.uint8).tobytes(), 9))

def score(rule):
    out = []
    for seed in range(SEEDS):
        rng = np.random.default_rng(seed)
        st = evolve(rule, rng.integers(0, 2, WIDTH, dtype=np.uint8), START + WIN)
        d, m = defects(st[START:])
        if d == 0:
            out.append((0.0, 0.0, 0.0)); continue
        rand = rng.random(m.shape) < d
        s = max(0.0, 1 - cz(m) / cz(rand))
        out.append((s * H(d), d, s))
    return tuple(float(np.mean(x)) for x in zip(*out))

if __name__ == "__main__":
    rows = sorted(((*score(g[0]), g) for g in classes()), reverse=True)
    print(f"{'score':>6} {'d':>6} {'s':>6}  rules")
    for sc, d, s, g in rows[:12]:
        print(f"{sc:6.3f} {d:6.3f} {s:6.3f}  {g}")
    for key in (110, 54, 30, 184):
        i = next(i for i, r in enumerate(rows) if key in r[3])
        print(f"rule {key}: rank {i + 1}, score {rows[i][0]:.3f}, d {rows[i][1]:.3f}, s {rows[i][2]:.3f}")
    with open("metric3_ranking.txt", "w") as f:
        for sc, d, s, g in rows:
            f.write(f"{sc:.4f}\t{d:.4f}\t{s:.4f}\t{g}\n")
