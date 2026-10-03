"""Cycle 88: multi-colour ants. A rule string like "LLRR" gives n colours; on colour k the ant turns as rule[k]
says, the cell advances to colour (k+1) mod n, and the ant steps forward. "RL" is Langton's ant.
Claim from the literature: LLRR keeps returning to bilaterally symmetric patterns.
Prediction (written first): within the first 50,000 steps from an empty grid, LLRR's pattern is EXACTLY mirror-
symmetric (about some vertical or horizontal line) at some step t > 0; and the plain RL ant never is, for t > 0
(control). Symmetry is checked every step on the set of non-zero cells (with colours)."""

def run_check(rule, steps):
    x = y = 0; d = 0; n = len(rule); grid = {}; hits = []
    xmin = xmax = ymin = ymax = 0
    for t in range(1, steps + 1):
        c = grid.get((x, y), 0)
        d = (d + (1 if rule[c] == "R" else -1)) % 4
        c2 = (c + 1) % n
        if c2: grid[(x, y)] = c2
        else: grid.pop((x, y), None)
        x += (0, 1, 0, -1)[d]; y += (-1, 0, 1, 0)[d]
        if t % 2 == 0 and grid:
            xs = [p[0] for p in grid]; ys = [p[1] for p in grid]
            sx = min(xs) + max(xs); sy = min(ys) + max(ys)          # mirror line at sx/2 (vertical) or sy/2
            if all(grid.get((sx - a, b)) == v for (a, b), v in grid.items()): hits.append((t, "vertical"))
            elif all(grid.get((a, sy - b)) == v for (a, b), v in grid.items()): hits.append((t, "horizontal"))
    return hits

if __name__ == "__main__":
    import sys
    llrr = run_check("LLRR", 50_000)
    rl = run_check("RL", 50_000)
    print(f"LLRR symmetric at {len(llrr)} steps; first few: {llrr[:6]}")
    print(f"RL   symmetric at {len(rl)} steps; first few: {rl[:6]}")
    held = len(llrr) > 0 and len(rl) == 0
    print("PREDICTION", "HELD" if held else "FAILED")

# --- revised question, asked AFTER the prediction failed (so not a prediction): tiny patterns are symmetric by
# accident (RL is symmetric at steps 2-48). Do symmetric moments persist once the pattern has >= 100 cells?
def sizes_at_symmetry(rule, steps):
    x = y = 0; d = 0; n = len(rule); grid = {}; out = []
    for t in range(1, steps + 1):
        c = grid.get((x, y), 0); d = (d + (1 if rule[c] == "R" else -1)) % 4; c2 = (c + 1) % n
        if c2: grid[(x, y)] = c2
        else: grid.pop((x, y), None)
        x += (0, 1, 0, -1)[d]; y += (-1, 0, 1, 0)[d]
        if t % 2 == 0 and len(grid) >= 100:
            xs = [p[0] for p in grid]; ys = [p[1] for p in grid]; sx = min(xs) + max(xs); sy = min(ys) + max(ys)
            if all(grid.get((sx - a, b)) == v for (a, b), v in grid.items()) or \
               all(grid.get((a, sy - b)) == v for (a, b), v in grid.items()):
                out.append((t, len(grid)))
    return out
if __name__ == "__main__":
    big_llrr = sizes_at_symmetry("LLRR", 50_000); big_rl = sizes_at_symmetry("RL", 50_000)
    print(f"REVISED: LLRR symmetric with >=100 cells at {len(big_llrr)} steps; last: {big_llrr[-3:]}")
    print(f"REVISED: RL   symmetric with >=100 cells at {len(big_rl)} steps")
