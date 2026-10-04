"""Dots and Boxes on 3x3 dots (2x2 boxes), solved exactly (cycle 195). Lines 0..5 horizontal (row r = 0..2, col c =
0..1 -> 2r + c), 6..11 vertical (row r = 0..1, col c = 0..2 -> 6 + 3r + c). Box (i, j) uses H(i,j), H(i+1,j),
V(i,j), V(i,j+1). value(mask) = best final (mover's boxes - opponent's) from here, over the boxes still to come."""
import json
from functools import lru_cache
from pathlib import Path
H = lambda r, c: 2 * r + c
V = lambda r, c: 6 + 3 * r + c
BOXES = [(H(i, j), H(i + 1, j), V(i, j), V(i, j + 1)) for i in range(2) for j in range(2)]
def made(mask, e):                                   # boxes completed by drawing line e onto mask
    return sum(1 for b in BOXES if e in b and all(mask >> x & 1 for x in b if x != e))
@lru_cache(None)
def value(mask):
    if mask == (1 << 12) - 1: return 0
    best = -99
    for e in range(12):
        if mask >> e & 1: continue
        k = made(mask, e); t = mask | 1 << e
        v = k + value(t) if k else -value(t)        # complete a box: move again; else the opponent moves
        best = max(best, v)
    return best
v0 = value(0)
print(f"first player's best margin with perfect play: {v0:+d} (so {'first' if v0 > 0 else 'second' if v0 < 0 else 'neither'} player wins)")
good = [e for e in range(12) if -value(1 << e) == v0]
print(f"opening lines that keep that margin: {good}; positions solved: {value.cache_info().currsize}")
print("first player's margin after each opening:", {e: -value(1 << e) for e in range(12)})   # cycle 195: inside = 0, a draw
(Path(__file__).resolve().parent / "boxes.json").write_text(json.dumps({"v0": v0, "good": good}), encoding="utf-8")
print("PREDICTION HELD" if v0 < 0 else "PREDICTION FAILED")
