"""5-flip search in a THREE-tile (42-cell) window, looking for the missing D, F, H.
Two phases to fit in memory: (1) chunked cheap filter: alive + compact (span <= 60) at T;
(2) re-evolve survivors with history and test EXACT periodicity (as glider_search3).
Prediction (written first): D appears (it's the slowest-moving small one we lack); F/H stay missing."""
import itertools, time, sys
from fractions import Fraction as Fr
import numpy as np

TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
NT = 24; W = 14 * NT; OFF = 14 * (NT // 2) - 7; T = 400; PMAX = 120; REPS = 3; K = 5; WIN = 42
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
CAT = {Fr(2, 3): "A", Fr(-1, 2): "B", Fr(0): "C", Fr(1, 5): "D", Fr(-4, 15): "E",
       Fr(-1, 9): "F", Fr(-1, 3): "G", Fr(-9, 46): "H"}
def step(r): return TABLE[4 * np.roll(r, 1, axis=-1) + 2 * r + np.roll(r, -1, axis=-1)]
def span(cells):
    c = np.sort(cells); g = np.diff(np.concatenate([c, [c[0] + W]])); return W - g.max() + 1

base = np.tile(TILE, NT)
clean_T = base.copy()
for _ in range(T): clean_T = step(clean_T)

def seeded(combos):
    rows = np.repeat(base[None, :], len(combos), axis=0)
    for i, c in enumerate(combos): rows[i, [OFF + x for x in c]] ^= 1
    return rows

t0 = time.time(); survivors = []; total = 0
gen = itertools.combinations(range(WIN), K)
while True:
    chunk = list(itertools.islice(gen, 20000))
    if not chunk: break
    rows = seeded(chunk)
    for _ in range(T): rows = step(rows)
    d = rows != clean_T
    for i in np.nonzero(d.any(axis=1))[0]:
        if span(np.nonzero(d[i])[0]) <= 60: survivors.append(chunk[i])
    total += len(chunk)
    print(f"  {total:7d} done, {len(survivors)} compact survivors, {time.time() - t0:.0f}s", flush=True)

print(f"phase 2: {len(survivors)} survivors", flush=True)
found, aperiodic = {}, 0
for s in range(0, len(survivors), 2000):
    chunk = survivors[s:s + 2000]; rows = seeded(chunk); clean = base.copy(); hist = []
    for t in range(1, T + 1):
        rows = step(rows); clean = step(clean)
        if t > T - REPS * PMAX - 1: hist.append(rows != clean)
    hist = np.stack(hist, axis=1)
    for i, c in enumerate(chunk):
        last = hist[i, -1]; idx = np.nonzero(last)[0]; hit = None
        for p in range(1, PMAX + 1):
            prev = hist[i, -1 - p]; pidx = np.nonzero(prev)[0]
            if pidx.size != idx.size: continue
            for dd in {int(idx[0]) - int(j) for j in pidx[:3]}:
                # cycle 32: must repeat over REPS consecutive periods, not just once
                if all(np.array_equal(np.roll(hist[i, -1 - (r + 1) * p], dd), hist[i, -1 - r * p]) for r in range(REPS)):
                    hit = (p, (dd + W // 2) % W - W // 2); break
            if hit: break
        if not hit: aperiodic += 1; continue
        v = Fr(hit[1], hit[0]); name = CAT.get(v, f"new? {v}")
        found.setdefault(name, []).append((c, hit))
for name in sorted(found):
    it = found[name]; print(f"  {name:>10}: {len(it):6d} patterns, period {it[0][1][0]} shift {it[0][1][1]:+d}, e.g. {it[0][0]}")
print(f"compact-but-not-periodic: {aperiodic}")
print("catalogue types NOT found:", [n for n in "ABCDEFGH" if n not in found])
print(f"total time {time.time() - t0:.0f}s")
