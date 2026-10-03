"""Cycle 2: can a metric put Rule 110 on top?

Hypothesis (written BEFORE running): complex (class 4) rules have long
transients - gliders collide and annihilate for thousands of steps, so the
pattern keeps getting MORE compressible over time. Chaotic rules stay flat-high,
simple rules settle almost immediately. Score = relative drop in compressed
size between an early window and a late window.
Prediction: 110 and 54 classes in the top 5.
"""
import zlib
import numpy as np
from eca import classes

WIDTH, STEPS, WIN = 1001, 6000, 200   # odd width: see cycle-1 XOR-annihilation bug
EARLY, LATE = 200, STEPS - WIN

def evolve(rule, row, steps):
    table = np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)
    out = np.empty((steps + 1, row.size), dtype=np.uint8)
    out[0] = row
    for t in range(steps):
        r = out[t]
        out[t + 1] = table[4 * np.roll(r, 1) + 2 * r + np.roll(r, -1)]
    return out

def csize(block):
    return len(zlib.compress(np.packbits(block).tobytes(), 9))

def score(rule, seeds=3):
    drops, lates = [], []
    for s in range(seeds):
        row = np.random.default_rng(s).integers(0, 2, WIDTH, dtype=np.uint8)
        st = evolve(rule, row, STEPS)
        early, late = csize(st[EARLY:EARLY + WIN]), csize(st[LATE:LATE + WIN])
        drops.append((early - late) / early)
        lates.append(late)
    return float(np.mean(drops)), float(np.mean(lates))

if __name__ == "__main__":
    noise = csize(np.random.default_rng(99).integers(0, 2, (WIN, WIDTH), dtype=np.uint8))
    rows = []
    for g in classes():
        drop, late = score(g[0])
        rows.append((drop, late / noise, g))
    rows.sort(reverse=True)
    print(f"{'drop':>6} {'late':>6}  rules")
    for drop, late, g in rows[:15]:
        print(f"{drop:6.3f} {late:6.3f}  {g}")
    rank = {tuple(g): i + 1 for i, (_, _, g) in enumerate(rows)}
    for key in (110, 54, 30):
        g = next(g for _, _, g in rows if key in g)
        print(f"rule {key} class rank: {rank[tuple(g)]} of {len(rows)}")
    with open("transients_ranking.txt", "w") as f:
        for drop, late, g in rows:
            f.write(f"{drop:.4f}\t{late:.4f}\t{g}\n")
