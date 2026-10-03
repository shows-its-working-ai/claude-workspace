"""Cycle 76: cycle 75 showed grouping by SPEED hid a second glider (E under E-bar). Does it hide others?
Prediction (written first, about the world): regrouping every hit by exact (period, shift) shows MORE than one
type at B's speed -1/2 (the catalogue lists B-bar^n and B-hat^n there too). Same 24,157-seed search.
For each speed, every distinct (period, shift) is listed with its seed count, simplest seed and defect size."""
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
    if hit: groups.setdefault(hit, []).append((c, int(idx.size), int(span(idx))))
by_speed = {}
for (p, d), items in groups.items(): by_speed.setdefault(Fr(d, p), []).append(((p, d), items))
for v in sorted(by_speed):
    print(f"speed {str(v):>6}:")
    for (p, d), items in sorted(by_speed[v]):
        simplest = min(items, key=lambda t: len(t[0]))
        sizes = sorted({(n, w) for _, n, w in items})
        print(f"   (period {p:3d}, shift {d:+4d}): {len(items):5d} seeds; simplest {simplest[0]}; "
              f"defect cells/width {sizes[:4]}{' ...' if len(sizes) > 4 else ''}")
multi = [str(v) for v in by_speed if len(by_speed[v]) > 1]
print("speeds with more than one (period, shift):", multi)

# which -6/12 glider is it? Published f1_1 phases (arXiv 0706.3348 appendix), variants A-C each.
BBAR = ["1111100010110111100110", "1111100001000110010110", "1111101111110000111000"]
BHAT = ["111110001011011110011001111111000100110", "111110000100011001011010110011000100110",
        "111110111111000011100000011111000100110"]
def found_in(seed, strs, n=120):
    row = base.copy(); row[[OFF + x for x in seed]] ^= 1
    for _ in range(T): row = step(row)
    hit = set()
    for _ in range(n):
        s = "".join(map(str, row)); s += s[:60]; hit |= {x for x in strs if x in s}; row = step(row)
    return len(hit)
def in_ether(strs):
    row = base.copy(); hit = set()
    for _ in range(28): s = "".join(map(str, row)); s += s[:60]; hit |= {x for x in strs if x in s}; row = step(row)
    return len(hit)
odd = min(groups[(12, -6)], key=lambda t: len(t[0]))[0]
print(f"\nthe (12,-6) seed {odd}: B-bar strings {found_in(odd, BBAR)}/3, B-hat strings {found_in(odd, BHAT)}/3")
print(f"control: ordinary B seed (7, 14): B-bar {found_in((7, 14), BBAR)}/3, B-hat {found_in((7, 14), BHAT)}/3")
print(f"control: pure ether: B-bar {in_ether(BBAR)}/3, B-hat {in_ether(BHAT)}/3")
ok = found_in(odd, BBAR) == 3 and found_in(odd, BHAT) == 0 and found_in((7, 14), BBAR) == 0 and in_ether(BBAR) == 0
print("B-BAR CONFIRMED" if ok else "B-BAR NOT CONFIRMED")
