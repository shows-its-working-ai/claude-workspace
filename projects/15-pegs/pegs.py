"""Cycle 145: triangle peg solitaire (rows of 1..5 holes, 15 total). For every position (bitmask of pegs) compute
whether a single-peg finish is reachable, by memoised search. Report per starting empty hole, and the number of
positions overall from which one peg is reachable."""
import json, sys
from functools import lru_cache
from pathlib import Path
HOLES = [(r, c) for r in range(5) for c in range(r + 1)]
IDX = {h: i for i, h in enumerate(HOLES)}
DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)]          # triangular grid neighbours
JUMPS = []                                                         # (from, over, to)
for (r, c) in HOLES:
    for dr, dc in DIRS:
        o, t = (r + dr, c + dc), (r + 2 * dr, c + 2 * dc)
        if o in IDX and t in IDX: JUMPS.append((IDX[(r, c)], IDX[o], IDX[t]))
FULL = (1 << 15) - 1
@lru_cache(maxsize=None)
def solvable(b):
    if bin(b).count("1") == 1: return True
    return any(b >> f & 1 and b >> o & 1 and not b >> t & 1 and solvable(b & ~(1 << f) & ~(1 << o) | (1 << t)) for f, o, t in JUMPS)
if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    per = [solvable(FULL & ~(1 << i)) for i in range(15)]
    for r in range(5): print("   " * (4 - r) + "  ".join("yes" if per[IDX[(r, c)]] else " no" for c in range(r + 1)))
    good = sum(solvable(b) for b in range(1, FULL + 1))
    print(f"jumps on the board: {len(JUMPS)}; positions with a one-peg finish: {good} of {FULL}")
    print("PREDICTION", "HELD" if all(per) else "FAILED", "(every starting hole can finish with one peg)")
    (Path(__file__).resolve().parent / "pegs.json").write_text(json.dumps({"per_start": per, "good": good}), encoding="utf-8")
