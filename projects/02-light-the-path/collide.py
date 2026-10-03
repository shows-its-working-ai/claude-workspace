"""Glider COLLISION search. Do the missing gliders (D, F, H) form when known ones collide?
Prediction (written first): at least one collision produces D, F or H.
Pairs arranged to meet; for each: separations x tile-multiples, and a 0-13 step launch delay for the second
glider (placed at the ether's CURRENT phase). After the dust settles, each surviving cluster is identified by
the strict test: same (period, shift) for 3 consecutive periods, compared within the cluster's own region."""
import itertools, time
from fractions import Fraction as Fr
import numpy as np

TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
NT = 40; W = 14 * NT; T = 900; PMAX = 120; REPS = 3
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
SEEDS = {"A": [0, 5], "B": [7, 14], "C": [6, 23], "E": [6], "G": [2, 18]}
CAT = {Fr(2, 3): "A", Fr(-1, 2): "B", Fr(0): "C", Fr(1, 5): "D", Fr(-4, 15): "E", Fr(-1, 9): "F", Fr(-1, 3): "G", Fr(-9, 46): "H"}
def step(r): return TABLE[4 * np.roll(r, 1, axis=-1) + 2 * r + np.roll(r, -1, axis=-1)]
base = np.tile(TILE, NT)
SHIFT = next(d for d in range(W) if np.array_equal(np.roll(base, d), step(base)))
PAIRS = [("A", x) for x in "BCEG"] + [("C", x) for x in "BEG"] + [("E", "B"), ("E", "G"), ("G", "B")]
configs = [(l, r, sep, delay) for l, r in PAIRS for sep in range(2, 7) for delay in range(14)]

rows = np.repeat(base[None, :], len(configs), axis=0)
L0 = 14 * 8
for i, (l, r, sep, delay) in enumerate(configs):
    rows[i, [L0 + o for o in SEEDS[l]]] ^= 1
clean = base.copy(); hist = []; t0 = time.time()
for t in range(T + 1):
    for i, (l, r, sep, delay) in enumerate(configs):          # launch the right-hand glider after `delay` steps
        if t == delay:
            for o in SEEDS[r]: rows[i, (L0 + 14 * sep + o + SHIFT * t) % W] ^= 1
    if t > T - REPS * PMAX - 1: hist.append(rows != clean)
    rows = step(rows); clean = step(clean)
hist = np.stack(hist, axis=1); print(f"{len(configs)} collisions x {T} steps in {time.time() - t0:.0f}s")

def clusters(cells, gap=30):
    c = np.sort(cells); out, cur = [], [c[0]]
    for x in c[1:]:
        if x - cur[-1] > gap: out.append(cur); cur = [x]
        else: cur.append(x)
    out.append(cur)
    if len(out) > 1 and out[0][0] + W - out[-1][-1] <= gap: out[0] = out.pop() + out[0]
    return out

def identify(i, cl):
    region = np.zeros(W, bool)
    for x in cl:
        for k in range(-12, 13): region[(x + k) % W] = True
    last = hist[i, -1]
    for p in range(1, PMAX + 1):
        prev = hist[i, -1 - p]
        for d in range(-40, 41):
            if all(np.array_equal(np.roll(hist[i, -1 - (r + 1) * p], d)[np.roll(region, d * 0)], hist[i, -1 - r * p][region]) for r in range(REPS)):
                return Fr(d, p)
    return None

found, outcomes = {}, {}
for i, cfg in enumerate(configs):
    cells = np.nonzero(hist[i, -1])[0]
    if cells.size == 0: outcomes["annihilated"] = outcomes.get("annihilated", 0) + 1; continue
    cls = clusters(cells)
    if any(max(c) - min(c) > 80 for c in cls): outcomes["chaotic/spread"] = outcomes.get("chaotic/spread", 0) + 1; continue
    names = []
    for cl in cls:
        v = identify(i, cl)
        names.append(CAT.get(v, f"?{v}") if v is not None else "aperiodic")
    key = "+".join(sorted(names)); outcomes[key] = outcomes.get(key, 0) + 1
    for n in names:
        if n in ("D", "F", "H") or n.startswith("?"): found.setdefault(n, []).append(cfg)
print("outcomes:"); [print(f"  {k:28s} {v}") for k, v in sorted(outcomes.items(), key=lambda kv: -kv[1])]
print("new/missing types produced:", {k: v[:3] for k, v in found.items()} or "none")
