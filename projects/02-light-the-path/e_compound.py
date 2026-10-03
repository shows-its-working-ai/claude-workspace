"""Cycle 55: what is the 36-cell object moving at E's speed (from E+G collisions, cycle 54)?
Prediction (written first): it is two E gliders packed together (Martinez's E^2): its period and shift equal
E's, and placing two lone E seeds at the right spacing reproduces it cell for cell."""
import numpy as np
TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
step = lambda r: TABLE[4 * np.roll(r, 1, axis=-1) + 2 * r + np.roll(r, -1, axis=-1)]
NT = 120; W = 14 * NT; base = np.tile(TILE, NT)
SHIFT = next(d for d in range(W) if np.array_equal(np.roll(base, d), step(base)))
SEEDS = {"E": [6], "G": [2, 18]}; L0 = 14 * 8

def run(seed_fn, T):
    row, clean = base.copy(), base.copy()
    for t in range(T + 1):
        seed_fn(t, row)
        if t == T: return row, clean
        row = step(row); clean = step(clean)

def collision(sep, delay):
    def f(t, row):
        if t == 0: row[[L0 + o for o in SEEDS["E"]]] ^= 1
        if t == delay:
            for o in SEEDS["G"]: row[(L0 + 14 * sep + o + SHIFT * t) % W] ^= 1
    return f

def period(row, clean, pmax=200):
    """exact (p, d) of the whole defect: 3 consecutive periods must match."""
    hist = []
    for _ in range(3 * pmax + 1):
        hist.append(row != clean); row = step(row); clean = step(clean)
    for p in range(1, pmax + 1):
        for d in range(-60, 61):
            if all(np.array_equal(np.roll(hist[r * p], d), hist[(r + 1) * p]) for r in range(3)): return p, d
    return None

def defect_profile(row, clean):
    x = np.nonzero(row != clean)[0]
    if x.max() - x.min() > W / 2: x = np.where(x < W / 2, x + W, x)
    return int(x.min()), "".join("#" if v else "." for v in np.isin(np.arange(x.min(), x.max() + 1) % W, x % W))

T = 3600
lone = run(lambda t, r: r.__setitem__(L0 + 6, r[L0 + 6] ^ 1) if t == 0 else None, T)
print("lone E:   ", period(*lone), defect_profile(*lone)[1], int((lone[0] != lone[1]).sum()), "cells")
targets = {}
for sep, delay in [(4, 4), (5, 4)]:
    obj = run(collision(sep, delay), T)
    print(f"E+G {sep},{delay}:", period(*obj), defect_profile(*obj)[1], int((obj[0] != obj[1]).sum()), "cells")
    targets[(sep, delay)] = obj

# Rebuild from two lone E seeds, ALL candidates batched: second E at offset k = 1..80 cells, launch delay 0..29.
hits = {}
CANDS = [(k, dl) for k in range(1, 81) for dl in range(30)]
rows = np.repeat(base[None, :], len(CANDS), axis=0); rows[:, L0 + 6] ^= 1
clean = base.copy(); TB = 900
for t in range(TB + 30):
    for j, (k, dl) in enumerate(CANDS):
        if t == dl: rows[j, (L0 + 6 + k + SHIFT * t) % W] ^= 1
    if t >= TB:                                                   # 30 consecutive phases = one full E period
        cur = rows != clean
        for key, obj in targets.items():
            tgt = obj[0] != obj[1]; n = int(tgt.sum()); b0 = int(np.nonzero(tgt)[0][0])
            for j in np.nonzero(cur.sum(axis=1) == n)[0]:
                a = np.nonzero(cur[j])[0]
                if any(np.array_equal(np.roll(cur[j], b0 - int(x)), tgt) for x in a):
                    hits.setdefault(key, []).append(CANDS[j])
    rows = step(rows); clean = step(clean)
for key in targets: print(f"two-E rebuild of {key}:", sorted(set(hits.get(key, [])))[:5] or "NONE")
