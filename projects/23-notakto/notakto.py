"""Notakto on one 3x3 board, solved exactly (cycle 192). A position = 9-bit mask of crosses. Whoever completes a line
loses, so a move that makes a line is never taken while another exists; with no safe move you must move and lose."""
import json
from functools import lru_cache
from pathlib import Path
LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
def dead(m): return any(all(m >> i & 1 for i in L) for L in LINES)
@lru_cache(None)
def wins(m):                                         # can the player to move force a win from mask m (no line yet)?
    return any(not dead(m | 1 << i) and not wins(m | 1 << i) for i in range(9) if not m >> i & 1)
first = [i for i in range(9) if not dead(1 << i) and not wins(1 << i)]
reach = set(); stack = [0]
while stack:
    m = stack.pop()
    if m in reach: continue
    reach.add(m)
    for i in range(9):
        t = m | 1 << i
        if not m >> i & 1 and not dead(t): stack.append(t)
print(f"first player wins: {wins(0)}; winning first moves: {first}; safe positions: {len(reach)}")
(Path(__file__).resolve().parent / "notakto.json").write_text(json.dumps({str(m): wins(m) for m in sorted(reach)}), encoding="utf-8")
print("PREDICTION HELD" if wins(0) and first == [4] else "PREDICTION FAILED")
