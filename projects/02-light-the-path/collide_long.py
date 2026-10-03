"""Follow-up to collide.py (cycle 54): what are the 29 'compact but aperiodic' outcomes?
Prediction (written first): given 4x more time on a 3x wider ring, most of them settle into known gliders
(slow wreckage), and none is a gun (a gun would keep making new clusters forever).
Method: rerun every collision, find those that were compact-but-aperiodic at step 900, then run THOSE to
step 3600 on a 1680-wide ring, logging cluster count and defect size, and identify what is left."""
import time
from fractions import Fraction as Fr
import numpy as np

TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
SEEDS = {"A": [0, 5], "B": [7, 14], "C": [6, 23], "E": [6], "G": [2, 18]}
CAT = {Fr(2, 3): "A", Fr(-1, 2): "B", Fr(0): "C", Fr(1, 5): "D", Fr(-4, 15): "E", Fr(-1, 9): "F", Fr(-1, 3): "G", Fr(-9, 46): "H"}
PAIRS = [("A", x) for x in "BCEG"] + [("C", x) for x in "BEG"] + [("E", "B"), ("E", "G"), ("G", "B")]
CONFIGS = [(l, r, sep, delay) for l, r in PAIRS for sep in range(2, 7) for delay in range(14)]
PMAX, REPS, L0 = 120, 3, 14 * 8
step = lambda r: TABLE[4 * np.roll(r, 1, axis=-1) + 2 * r + np.roll(r, -1, axis=-1)]

def run(configs, NT, T, checkpoints=()):
    W = 14 * NT; base = np.tile(TILE, NT)
    shift = next(d for d in range(W) if np.array_equal(np.roll(base, d), step(base)))
    rows = np.repeat(base[None, :], len(configs), axis=0)
    for i, (l, r, sep, delay) in enumerate(configs): rows[i, [L0 + o for o in SEEDS[l]]] ^= 1
    clean = base.copy(); hist, snaps = [], {}
    for t in range(T + 1):
        for i, (l, r, sep, delay) in enumerate(configs):
            if t == delay:
                for o in SEEDS[r]: rows[i, (L0 + 14 * sep + o + shift * t) % W] ^= 1
        if t in checkpoints: snaps[t] = rows != clean
        if t > T - REPS * PMAX - 1: hist.append(rows != clean)
        rows = step(rows); clean = step(clean)
    return W, np.stack(hist, axis=1), snaps

def clusters(cells, W, gap=30):
    if cells.size == 0: return []
    c = np.sort(cells); out, cur = [], [c[0]]
    for x in c[1:]:
        if x - cur[-1] > gap: out.append(cur); cur = [x]
        else: cur.append(x)
    out.append(cur)
    if len(out) > 1 and out[0][0] + W - out[-1][-1] <= gap: out[0] = out.pop() + out[0]
    return out
span = lambda c, W: (max(c) - min(c)) if max(c) - min(c) < W / 2 else (min(x if x > W / 2 else x + W for x in c) and
       max(x if x > W / 2 else x + W for x in c) - min(x if x > W / 2 else x + W for x in c))

def identify(h, cl, W):
    region = np.zeros(W, bool)
    for x in cl:
        for k in range(-12, 13): region[(x + k) % W] = True
    for p in range(1, PMAX + 1):
        for d in range(-40, 41):
            if all(np.array_equal(np.roll(h[-1 - (r + 1) * p], d)[region], h[-1 - r * p][region]) for r in range(REPS)):
                return Fr(d, p)
    return None

def classify(h, W):
    cells = np.nonzero(h[-1])[0]
    if cells.size == 0: return "annihilated"
    cls = clusters(cells, W)
    if any(span(c, W) > 80 for c in cls): return "chaotic/spread"
    names = []
    for cl in cls:
        v = identify(h, cl, W); names.append(CAT.get(v, f"?{v}") if v is not None else "aperiodic")
    return "+".join(sorted(names))

t0 = time.time()
W1, h1, _ = run(CONFIGS, 40, 900)
first = {i: classify(h1[i], W1) for i in range(len(CONFIGS))}
aper = [i for i, k in first.items() if "aperiodic" in k]
print(f"pass 1: {len(CONFIGS)} collisions, {len(aper)} with an aperiodic cluster ({time.time() - t0:.0f}s)")
CHK = (900, 1800, 2700, 3600)
W2, h2, snaps = run([CONFIGS[i] for i in aper], 120, 3600, CHK)
tally, newtypes = {}, []
for j, i in enumerate(aper):
    traj = [len(clusters(np.nonzero(snaps[t][j])[0], W2)) for t in CHK]
    size = [int(snaps[t][j].sum()) for t in CHK]
    k = classify(h2[j], W2); tally[k] = tally.get(k, 0) + 1
    if any(n in k for n in ("D", "F", "H", "?")): newtypes.append((CONFIGS[i], k))
    print(f"  {str(CONFIGS[i]):22s} 900: {first[i]:18s} -> 3600: {k:28s} clusters {traj} defect cells {size}")
print("at step 3600:"); [print(f"  {k:28s} {v}") for k, v in sorted(tally.items(), key=lambda kv: -kv[1])]
growing = sum(1 for j in range(len(aper)) if len(clusters(np.nonzero(snaps[3600][j])[0], W2)) > len(clusters(np.nonzero(snaps[1800][j])[0], W2)) + 1)
print("cluster count still growing after 1800:", growing)
print("new/missing types:", newtypes or "none")
print(f"total {time.time() - t0:.0f}s")
