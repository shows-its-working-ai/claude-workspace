"""Ant Golf levels (cycle 89). Langton's ant starts at (0,0) facing up on white. Before it runs, you paint up to a few
cells black inside a 9x9 area around it. Goal: the ant must step onto the target cell within LIMIT steps.
Par = the fewest painted cells that do it, found by EXHAUSTIVE search over all subsets of size 0, 1, 2, 3.
A level is kept if par is 2 or 3 (0 or 1 is too easy), and with few solutions at par (so it isn't luck).
Deterministic: same seed, same levels."""
import itertools, json, random
from pathlib import Path
D = Path(__file__).resolve().parent
R = 4; LIMIT = 100                                       # paintable area: x, y in -4..4
CELLS = [(x, y) for y in range(-R, R + 1) for x in range(-R, R + 1) if (x, y) != (0, 0)]

def reaches(black, goal, limit=LIMIT):
    """True if the ant steps onto goal within `limit` steps (start cell (0,0) doesn't count)."""
    b = set(black); x = y = 0; d = 0
    for _ in range(limit):
        if (x, y) in b: d = (d - 1) % 4; b.discard((x, y))
        else: d = (d + 1) % 4; b.add((x, y))
        x += (0, 1, 0, -1)[d]; y += (-1, 0, 1, 0)[d]
        if (x, y) == goal: return True
    return False

def par_and_count(goal, kmax=3):
    for k in range(kmax + 1):
        sols = [c for c in itertools.combinations(CELLS, k) if reaches(c, goal)]
        if sols: return k, len(sols), sols[0]
    return None, 0, None

if __name__ == "__main__":
    rng = random.Random(89)
    goals = [(x, y) for y in range(-6, 7) for x in range(-6, 7) if abs(x) + abs(y) >= 3]
    rng.shuffle(goals); levels = []
    for g in goals:
        if len(levels) == 8: break
        k, n, sol = par_and_count(g)
        if k in (2, 3) and n <= 40:
            levels.append({"goal": list(g), "par": k, "solutions_at_par": n, "example": [list(c) for c in sol]})
            print(f"goal {g}: par {k}, {n} solutions at par", flush=True)
    levels.sort(key=lambda L: (L["par"], -L["solutions_at_par"]))
    for i, L in enumerate(levels): L["name"] = f"Hole {i + 1}"
    (D / "levels.json").write_text(json.dumps(levels, indent=1), encoding="utf-8")
    print(len(levels), "levels")
