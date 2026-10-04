"""Langton's ant from an empty grid (cycle 175). Find where the highway starts: the first step t after which the
ant's moves repeat with period P and the squares it meets look the same (relative to it) each cycle."""
import json
from pathlib import Path
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]               # up, right, down, left (y grows downward)
def run(steps):
    black, x, y, d, trail = set(), 0, 0, 0, []
    for _ in range(steps):
        if (x, y) in black: d = (d - 1) % 4; black.discard((x, y))
        else: d = (d + 1) % 4; black.add((x, y))
        dx, dy = DIRS[d]; x += dx; y += dy; trail.append((x, y, d))
    return black, trail
N = 20000
black, trail = run(N)
def periodic_from(t, P):                                 # moves repeat from t to the end, shifted by a fixed vector
    sx, sy = trail[t + P][0] - trail[t][0], trail[t + P][1] - trail[t][1]
    return all(trail[i + P][2] == trail[i][2] and trail[i + P][0] - trail[i][0] == sx and trail[i + P][1] - trail[i][1] == sy
               for i in range(t, N - P)), (sx, sy)
found = None
for P in range(1, 300):
    ok, shift = periodic_from(N - 3 * P - 1, P)
    if ok: found = P; break
P = found
lo, hi = 0, N - 3 * P - 1                                 # earliest t from which it stays periodic (binary search)
while lo < hi:
    m = (lo + hi) // 2
    if periodic_from(m, P)[0]: hi = m
    else: lo = m + 1
shift = periodic_from(lo, P)[1]
print(f"period {P}, shift per period {shift}, highway from step {lo + 1}")
snap = {n: sorted(run(n)[0]) for n in (500, 5000, 11000)}
(Path(__file__).resolve().parent / "ant.json").write_text(json.dumps({"black": {str(k): v for k, v in snap.items()},
    "period": P, "start": lo + 1}), encoding="utf-8")
print("PREDICTION HELD" if P == 104 and sorted(map(abs, shift)) == [2, 2] and lo + 1 < 11000 else "PREDICTION FAILED")
