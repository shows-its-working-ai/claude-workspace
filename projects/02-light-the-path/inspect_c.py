"""Inspect the 'speed 1' survivor from glider_search4 before believing it."""
import numpy as np
TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
NT = 24; W = 14 * NT; OFF = 14 * (NT // 2) - 7
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
def step(r): return TABLE[4 * np.roll(r, 1) + 2 * r + np.roll(r, -1)]
base = np.tile(TILE, NT); row = base.copy(); row[[OFF + x for x in (3, 8, 11, 26, 41)]] ^= 1
clean = base.copy()
for t in range(1, 1201):
    row = step(row); clean = step(clean)
    if t in (50, 200, 398, 399, 400, 600, 1200):
        d = np.nonzero(row != clean)[0]
        print(f"t={t:4d}: {d.size:3d} defect cells at {d.tolist()[:12]}{'...' if d.size > 12 else ''}")
