"""Wider glider search: flip 1-4 cells in a TWO-tile (28-cell) window of Rule 110's ether,
evolve every candidate at once (numpy batch), keep defects alive and compact at t=300,
and classify each by drift speed against the published catalogue.
Prediction (written before running): finds B (-1/2) and D (1/5); F, G, H probably not."""
import itertools, time
from fractions import Fraction as Fr
import numpy as np

TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
NT = 24; W = 14 * NT; OFF = 14 * (NT // 2); T = 300; T1 = 150
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
CATALOGUE = {"A": Fr(2, 3), "B": Fr(-1, 2), "C": Fr(0), "D": Fr(1, 5), "E": Fr(-4, 15),
             "F": Fr(-1, 9), "G": Fr(-1, 3), "H": Fr(-9, 46)}

def step(rows):
    return TABLE[4 * np.roll(rows, 1, axis=1) + 2 * rows + np.roll(rows, -1, axis=1)]

base = np.tile(TILE, NT)
combos = [c for k in range(1, 5) for c in itertools.combinations(range(28), k)]
t0 = time.time()
rows = np.repeat(base[None, :], len(combos), axis=0)
for i, c in enumerate(combos):
    rows[i, [OFF + x for x in c]] ^= 1
clean = base.copy()
snap = None
for t in range(1, T + 1):
    rows = step(rows); clean = step(clean[None, :])[0]
    if t == T1:
        snap = rows != clean
diff = rows != clean
print(f"evolved {len(combos)} candidates x {T} steps on a {W}-ring in {time.time() - t0:.1f}s")

def circ(cells):
    c = np.sort(cells); gaps = np.diff(np.concatenate([c, [c[0] + W]]))
    i = np.argmax(gaps); span = W - gaps[i] + 1
    start = c[(i + 1) % len(c)]
    centre = (start + np.mean((c - start) % W)) % W
    return span, centre

found = {}
for i, c in enumerate(combos):
    d1, d2 = np.nonzero(snap[i])[0], np.nonzero(diff[i])[0]
    if d1.size == 0 or d2.size == 0: continue
    s1, c1 = circ(d1); s2, c2 = circ(d2)
    if s2 > 40 or s1 > 40: continue
    v = ((c2 - c1 + W / 2) % W - W / 2) / (T - T1)
    name = min(CATALOGUE, key=lambda k: abs(float(CATALOGUE[k]) - v))
    if abs(float(CATALOGUE[name]) - v) > 0.015: name = f"? v={v:+.3f}"
    found.setdefault(name, []).append((c, int(s2)))
for name in sorted(found, key=str):
    items = found[name]
    print(f"  {name:>12}: {len(items):5d} patterns, smallest k={min(len(x[0]) for x in items)}, e.g. flips {min(items, key=lambda x: len(x[0]))[0]}")
missing = [k for k in CATALOGUE if k not in found]
print("catalogue types NOT found:", missing)
