"""Cycle 83: are this page's ranks for Rule 110 (14th by randomness, 1st by transients) robust to the random starts?
They average only 4 and 3 starts. Predictions (written first):
  (1) under the cycle-1 randomness metric, 110's rank stays within +-3 of 14 across 5 fresh batches of 4 starts;
  (2) under the transients metric, 110 stays #1 in all 5 fresh batches of 3 starts.
CONTROL: batch 0 (the original seeds) must reproduce the published ranks exactly (14 and 1), so the reimplementation
(numpy evolution, same random-start code) is the same measurement."""
import random, zlib
import numpy as np
from eca import classes
import transients as tr
G = classes()
def evolve(rule, row, steps):
    tab = np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8); out = [row]
    for _ in range(steps): row = tab[4 * np.roll(row, 1) + 2 * row + np.roll(row, -1)]; out.append(row)
    return out
def complexity(rule, seed_list, width=257, steps=512):
    sc = []
    for s in seed_list:
        rng = random.Random(s); start = np.array([rng.randint(0, 1) for _ in range(width)], dtype=np.uint8)
        tail = evolve(rule, start, steps)[steps // 2:]
        raw = np.array(tail, dtype=np.uint8).tobytes()
        noise = bytes(rng.randint(0, 1) for _ in raw)
        sc.append(len(zlib.compress(raw, 9)) / len(zlib.compress(noise, 9)))
    return sum(sc) / len(sc)
def trans(rule, seed_list):
    drops, lates = [], []
    for s in seed_list:
        row = np.random.default_rng(s).integers(0, 2, tr.WIDTH, dtype=np.uint8); st = tr.evolve(rule, row, tr.STEPS)
        e, l = tr.csize(st[tr.EARLY:tr.EARLY + tr.WIN]), tr.csize(st[tr.LATE:tr.LATE + tr.WIN])
        drops.append((e - l) / e); lates.append(l)
    return float(np.mean(drops)), float(np.mean(lates))
def rank_of(scores):                                   # scores: {class index: sortable}, higher = rank 1
    order = sorted(scores, key=lambda k: scores[k], reverse=True); return order.index(next(i for i, g in enumerate(G) if 110 in g)) + 1
r1, r2 = [], []
for b in range(6):                                     # batch 0 = original seeds (control); 1-5 fresh
    s1 = list(range(4 * b, 4 * b + 4)) if b else [0, 1, 2, 3]
    s2 = list(range(3 * b + 100, 3 * b + 103)) if b else [0, 1, 2]
    r1.append(rank_of({i: complexity(g[0], s1) for i, g in enumerate(G)}))
    r2.append(rank_of({i: trans(g[0], s2) for i, g in enumerate(G)}))
    print(f"batch {b}{' (original seeds)' if b == 0 else ''}: randomness rank {r1[-1]}, transients rank {r2[-1]}", flush=True)
print("CONTROL", "OK" if (r1[0], r2[0]) == (14, 1) else f"MISMATCH {r1[0], r2[0]}")
print("(1) randomness within 14+-3:", "HELD" if all(11 <= r <= 17 for r in r1[1:]) else "FAILED", r1[1:])
print("(2) transients #1 every batch:", "HELD" if all(r == 1 for r in r2[1:]) else "FAILED", r2[1:])
