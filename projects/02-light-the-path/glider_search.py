"""Brute-force search for Rule 110 gliders: flip k cells inside one 14-cell window of the
ether and keep defects that survive 300 steps while staying compact (span <= 30).
A survivor's drift (cells moved per step, measured vs the ether) identifies its type."""
import itertools
import numpy as np

TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
W, T, OFF = 14 * 24, 300, 14 * 12
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)

def evolve(row):
    out = np.empty((T + 1, W), dtype=np.uint8); out[0] = row
    for t in range(T):
        r = out[t]; out[t + 1] = TABLE[4 * np.roll(r, 1) + 2 * r + np.roll(r, -1)]
    return out

base = np.tile(TILE, 24)
clean = evolve(base)

def centre(diff_row):
    idx = np.nonzero(diff_row)[0]
    if idx.size == 0:
        return None
    # unwrap around the ring relative to the first defect cell
    ang = np.angle(np.exp(2j * np.pi * idx / W).mean())
    return (ang / (2 * np.pi) * W) % W, idx

found = {}
for k in (1, 2, 3):
    for flips in itertools.combinations(range(14), k):
        row = base.copy(); row[[OFF + f for f in flips]] ^= 1
        diff = evolve(row) != clean
        last = diff[-1]
        if not last.any():
            continue
        c_end, idx = centre(last)
        span = (idx.max() - idx.min() + 1) if idx.max() - idx.min() < W // 2 else W
        if span > 30:
            continue
        c_mid, _ = centre(diff[T // 2])
        v = ((c_end - c_mid + W / 2) % W - W / 2) / (T - T // 2)   # cells per step
        key = round(v, 3)
        found.setdefault(key, []).append((flips, int(last.sum()), int(span)))
print(f"searched {14 + 91 + 364} flip patterns; persistent compact defects by drift speed:")
for v, items in sorted(found.items()):
    print(f"  speed {v:+.3f} cells/step: {len(items):3d} patterns, e.g. flips {items[0][0]} (n={items[0][1]}, span={items[0][2]})")
