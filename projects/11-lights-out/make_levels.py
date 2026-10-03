"""Lights Out levels (cycle 99). Every board is MADE by pressing a random set of cells on a dark board, so it is
solvable by construction. Par = the fewest presses = the lightest of its 4 solutions (lights.solve gives all 4).
Kept: par 3..12, laid out as a ladder. Deterministic: same seed, same levels. Solutions are not shipped."""
import json, random
from pathlib import Path
from lights import solve, apply
D = Path(__file__).resolve().parent
TARGET = [3, 4, 5, 5, 6, 7, 7, 8, 9, 10, 11, 12]

def popcount(x): return bin(x).count("1")
rng = random.Random(99); pool = {}
while not all(t in pool for t in TARGET):
    presses = 0
    for i in rng.sample(range(25), rng.randint(3, 15)): presses |= 1 << i
    board = apply(presses)
    sols = solve(board); assert len(sols) == 4 and all(apply(x) == board for x in sols)
    par = min(popcount(x) for x in sols)
    pool.setdefault(par, []).append((board, min(sols, key=popcount)))
levels, used = [], {}
for t in TARGET:
    k = used.get(t, 0); board, best = pool[t][k]; used[t] = k + 1
    levels.append({"name": f"Level {len(levels) + 1}", "board": board, "par": t, "solution": best})
(D / "levels.json").write_text(json.dumps(levels, indent=1), encoding="utf-8")
print(len(levels), "levels; pars", [L["par"] for L in levels])
