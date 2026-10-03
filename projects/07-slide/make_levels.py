"""Generates Slide levels. You slide until a rock or the wall stops you; you must come to REST on the goal.
Each candidate grid is solved by breadth-first search (exact minimum moves = par). A level is kept only if:
par is in range, the goal is reachable, and it isn't trivial (enough distinct resting spots, and no straight-line
shortcut). Levels are sorted by par. Deterministic: same seed, same levels."""
import json, random
from collections import deque
from pathlib import Path
D = Path(__file__).resolve().parent
DIRS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

def slide(grid, r, c, d):
    dr, dc = DIRS[d]; H, W = len(grid), len(grid[0])
    while 0 <= r + dr < H and 0 <= c + dc < W and grid[r + dr][c + dc] != "#":
        r, c = r + dr, c + dc
    return r, c
def solve(grid, start, goal):
    """BFS over resting positions. Returns (par, path, number of reachable resting spots)."""
    prev = {start: None}; q = deque([start])
    while q:
        p = q.popleft()
        if p == goal: break
        for d in "UDLR":
            n = slide(grid, *p, d)
            if n != p and n not in prev: prev[n] = (p, d); q.append(n)
    if goal not in prev: return None, None, len(prev)
    path = []; p = goal
    while prev[p]: p, d = prev[p]; path.append(d)
    return len(path), "".join(reversed(path)), len(prev)

def candidate(rng, H=9, W=9, density=0.16):
    grid = [["#" if rng.random() < density else "." for _ in range(W)] for _ in range(H)]
    free = [(r, c) for r in range(H) for c in range(W) if grid[r][c] == "."]
    s, g = rng.sample(free, 2)
    return ["".join(row) for row in grid], s, g

TARGET = [5, 5, 6, 6, 7, 8, 9, 10, 11, 12, 13, 15]                # a difficulty ladder (par per level)
def make(n=12, seed=2026, lo=5, hi=16):
    rng = random.Random(seed); out = []; tried = 0
    while (len(out) < 600 or not all(any(L["par"] == t for L in out) for t in TARGET)) and tried < 400000:
        tried += 1
        grid, s, g = candidate(rng)
        par, path, spots = solve(grid, s, g)
        if par is None or not (lo <= par <= hi) or spots < 18: continue
        out.append({"grid": grid, "start": list(s), "goal": list(g), "par": par, "solution": path, "spots": spots})
    from quality import analyse                                   # cycle 68: prefer ONE shortest solution + a trap
    for L in out: L.update({k: v for k, v in analyse(L).items() if k in ("shortest_solutions", "traps")})
    pick, used = [], set()
    for t in TARGET:                                              # per rung: unique solution, then traps, then openness
        L = max((L for i, L in enumerate(out) if L["par"] == t and i not in used),
                key=lambda L: (L["shortest_solutions"] == 1, L["traps"] > 0, L["spots"]))
        used.add(out.index(L)); pick.append(L)
    return pick, tried
if __name__ == "__main__":
    levels, tried = make()
    for i, L in enumerate(levels): L["name"] = f"Level {i + 1}"
    (D / "levels.json").write_text(json.dumps(levels, indent=1), encoding="utf-8")
    print(f"{len(levels)} levels from {tried} candidates; pars:", [L["par"] for L in levels])
