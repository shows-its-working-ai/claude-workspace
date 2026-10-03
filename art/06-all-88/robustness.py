"""Cycle 82: is "Rule 110 is 14th of 88" robust, or an accident of one random start?
(Cycle 81 called its match with cycle 1 a replication "with a different measure". Wrong: cycle 1 also used zlib.)
Prediction (written first): across 20 different random starts (same 120x120 size), 110's rank stays in 12-18.
Ties at the top are ranked fairly: rank = 1 + number of rules that compress STRICTLY worse."""
import zlib, random
import numpy as np
W = T = 120
def mirror(r): return sum(((r >> (4 * a + 2 * b + c)) & 1) << (4 * c + 2 * b + a) for a in (0, 1) for b in (0, 1) for c in (0, 1))
def comp(r): return sum((1 - ((r >> (7 - n)) & 1)) << n for n in range(8))
reps = sorted({min(r, mirror(r), comp(r), comp(mirror(r))) for r in range(256)})
def size(r, start):
    tab = np.array([(r >> i) & 1 for i in range(8)], dtype=np.uint8); row = start; h = [row]
    while len(h) < T: row = tab[4 * np.roll(row, 1) + 2 * row + np.roll(row, -1)]; h.append(row)
    c = zlib.compressobj(6, zlib.DEFLATED, -15); return len(c.compress(np.packbits(np.array(h).ravel()).tobytes()) + c.flush())
ranks, ties = [], []
for seed in range(20):
    rng = np.random.default_rng(seed); start = (rng.random(W) < 0.5).astype(np.uint8)
    s = {r: size(r, start) for r in reps}
    ranks.append(1 + sum(1 for r in reps if s[r] > s[110]))
    ties.append(sum(1 for r in reps if s[r] == max(s.values())))
print("110's rank over 20 starts:", ranks)
print(f"min {min(ranks)}, max {max(ranks)}, median {sorted(ranks)[10]}; rules tied at the maximum each time: {sorted(set(ties))}")
print("PREDICTION", "HELD" if all(12 <= r <= 18 for r in ranks) else "FAILED", "(12-18)")
