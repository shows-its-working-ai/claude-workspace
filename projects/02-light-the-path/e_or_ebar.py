"""Cycle 75: my glider search grouped hits by SPEED, so everything at -4/15 was called "E". E (period 15) and E-bar
(period 30) share that speed. Did the search ever find a TRUE E?
Prediction (written first, a claim about the world, not my code): yes, at least one of the 4-flip seeds is a
genuine period-15 E. Same search as glider_search3.py (all 1-4 flips in a 28-cell window), grouped by exact
(period, shift); any period-15 hit is then confirmed against the published E phase strings."""
import itertools, time
from fractions import Fraction as Fr
import numpy as np

TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
NT = 24; W = 14 * NT; OFF = 14 * (NT // 2); T = 400; PMAX = 120; REPS = 3
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
    if t > T - REPS * PMAX - 1: hist.append(rows != clean)        # keep the last PMAX+1 defect rows
hist = np.stack(hist, axis=1)                              # (candidates, PMAX+1, W)
print(f"{len(combos)} candidates, {T} steps, {time.time() - t0:.1f}s")

def span(cells):
    c = np.sort(cells); g = np.diff(np.concatenate([c, [c[0] + W]])); return W - g.max() + 1

def span(cells):
    c = np.sort(cells); g = np.diff(np.concatenate([c, [c[0] + W]])); return W - g.max() + 1
groups = {}
for i, c in enumerate(combos):
    last = hist[i, -1]; idx = np.nonzero(last)[0]
    if idx.size == 0 or span(idx) > 60: continue
    hit = None
    for p in range(1, PMAX + 1):
        prev = hist[i, -1 - p]; pidx = np.nonzero(prev)[0]
        if pidx.size != idx.size: continue
        for d in {(int(idx[0]) - int(j)) for j in pidx[:3]}:
            if all(np.array_equal(np.roll(hist[i, -1 - (r + 1) * p], d), hist[i, -1 - r * p]) for r in range(REPS)):
                hit = (p, (d + W // 2) % W - W // 2); break
        if hit: break
    if hit and Fr(hit[1], hit[0]) == Fr(-4, 15): groups.setdefault(hit, []).append(c)
for pd, seeds in sorted(groups.items()):
    print(f"speed -4/15 with (period, shift) = {pd}: {len(seeds)} seeds; simplest {min(seeds, key=len)}")

# confirm with published strings (arXiv 0706.3348 A.11 E, A.12 E-bar) for one seed of each (p, d)
E_STR = ["1111100000000100110", "1111100010000000110", "1111100010011000000", "1110000011000100110",
         "1111101000011100110", "1111100011100011010", "1111101100000100110", "1111100011110000110",
         "1111100010011001000", "1110110011000100110", "1111101111011100110", "1111100011100111010",
         "1111100010011010110", "1111111111000100110"]
EB_STR = ["111110000100011111010", "111110001000110011000", "111011011101011100110", "111110111111011111010",
          "111110001110000111000", "111110011111011100110", "111110001011000111010", "111110001001111100110",
          "111111001111000100110"]
def strings_found(seed, strs):
    row = base.copy(); row[[OFF + x for x in seed]] ^= 1
    for _ in range(T): row = step(row)
    found = set()
    for _ in range(60):
        s = "".join(map(str, row)); s += s[:60]; found |= {x for x in strs if x in s}; row = step(row)
    return len(found)
for pd, seeds in sorted(groups.items()):
    sd = min(seeds, key=len)
    print(f"  {pd} seed {sd}: published E strings {strings_found(sd, E_STR)}/{len(E_STR)}, "
          f"E-bar strings {strings_found(sd, EB_STR)}/{len(EB_STR)}")
true_e = [pd for pd in groups if pd[0] == 15]
print("TRUE E FOUND" if true_e else "NO TRUE E: every -4/15 hit is period 30 (E-bar)")
