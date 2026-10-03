"""Exact glider identification. A true glider is exactly periodic: its defect at step T equals
its defect at step T-p shifted by d cells. Speed = d/p as an exact Fraction, compared to the
catalogue with no tolerance. Survivors that are compact but NOT periodic are reported apart
(likely pairs or still-settling debris), not forced into a class.
Prediction (cycle 31, before running): B and D appear with 4 flips; F, G, H probably not."""
import itertools, time
from fractions import Fraction as Fr
import numpy as np

TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
NT = 24; W = 14 * NT; OFF = 14 * (NT // 2); T = 400; PMAX = 120
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
CAT = {Fr(2, 3): "A", Fr(-1, 2): "B", Fr(0): "C", Fr(1, 5): "D", Fr(-4, 15): "E",
       Fr(-1, 9): "F", Fr(-1, 3): "G", Fr(-9, 46): "H"}

def step(r): return TABLE[4 * np.roll(r, 1, axis=-1) + 2 * r + np.roll(r, -1, axis=-1)]

base = np.tile(TILE, NT)
combos = [c for k in range(1, 5) for c in itertools.combinations(range(28), k)]
rows = np.repeat(base[None, :], len(combos), axis=0)
for i, c in enumerate(combos): rows[i, [OFF + x for x in c]] ^= 1
clean = base.copy(); hist = []
t0 = time.time()
for t in range(1, T + 1):
    rows = step(rows); clean = step(clean)
    if t > T - PMAX - 1: hist.append(rows != clean)        # keep the last PMAX+1 defect rows
hist = np.stack(hist, axis=1)                              # (candidates, PMAX+1, W)
print(f"{len(combos)} candidates, {T} steps, {time.time() - t0:.1f}s")

def span(cells):
    c = np.sort(cells); g = np.diff(np.concatenate([c, [c[0] + W]])); return W - g.max() + 1

found, aperiodic, dead, spread = {}, 0, 0, 0
for i, c in enumerate(combos):
    last = hist[i, -1]; idx = np.nonzero(last)[0]
    if idx.size == 0: dead += 1; continue
    if span(idx) > 60: spread += 1; continue
    hit = None
    for p in range(1, PMAX + 1):
        prev = hist[i, -1 - p]; pidx = np.nonzero(prev)[0]
        if pidx.size != idx.size: continue
        for d in {(int(idx[0]) - int(j)) for j in pidx[:3]}:   # align first defect cell with an early one
            if np.array_equal(np.roll(prev, d), last):
                dd = (d + W // 2) % W - W // 2; hit = (p, dd); break
        if hit: break
    if not hit: aperiodic += 1; continue
    v = Fr(hit[1], hit[0]); name = CAT.get(v, f"new? {v}")
    found.setdefault(name, []).append((c, hit))
for name in sorted(found):
    it = found[name]; ex = min(it, key=lambda x: len(x[0]))
    print(f"  {name:>10}: {len(it):5d} patterns  period {ex[1][0]} shift {ex[1][1]:+d}  smallest k={len(ex[0])} e.g. {ex[0]}")
print(f"dead {dead}, spread {spread}, compact-but-not-periodic {aperiodic}")
print("catalogue types NOT found:", [n for n in "ABCDEFGH" if n not in found])
