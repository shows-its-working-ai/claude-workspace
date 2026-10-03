"""Nonogram pictures + a line solver that proves each one is solvable by logic alone.

A puzzle is accepted only if repeated line-by-line deduction (every placement of the blocks
consistent with the clues and the cells known so far; keep what ALL placements agree on)
fills the whole grid. That means: unique solution, and no guessing needed.
"""
import json
from functools import lru_cache

PICTURES = {  # '#' = filled. Drawn by hand.
    "Teacup": """
        ..#..#..
        ..#..#..
        ..#..#..
        ........
        #######.
        #.....##
        #.....##
        ######..
    """,
    "Key": """
        .###......
        ##.##.....
        #...######
        ##.##..#.#
        .###...###
    """,
    "Sailboat": """
        ....#.....
        ....##....
        ....###...
        ....####..
        ....#####.
        ....#.....
        ##########
        .########.
        ..######..
    """,
    "Cat": """
        #.......#.
        ##.....##.
        #########.
        #..###..#.
        #########.
        ###...###.
        .#######..
        ..#####...
    """,
    "Snail": """
        ...#####....
        ..##...##...
        .##.###.##..
        .#.##.#..#..
        .#.#..##.#.#
        .##.....##.#
        ..#######.##
        ############
    """,
    "Lighthouse": """
        ....##....
        ...####...
        ..######..
        ...#..#...
        ...####...
        ...#..#...
        ...####...
        ..#....#..
        ..######..
        ##########
    """,
}

def grid(pic):
    rows = [r.strip() for r in pic.strip().splitlines()]
    assert len({len(r) for r in rows}) == 1, "ragged picture"
    return [[1 if c == "#" else 0 for c in r] for r in rows]

def clues(line):
    out, run = [], 0
    for v in line:
        if v: run += 1
        elif run: out.append(run); run = 0
    if run: out.append(run)
    return out

def placements(clue, n, known):
    """All 0/1 lines of length n matching `clue` and agreeing with known (None = unknown)."""
    clue = tuple(clue)
    @lru_cache(None)
    def go(i, k):
        if k == len(clue):     # all blocks placed: the rest must be empty (and IS length n - i)
            return [(0,) * (n - i)] if all(known[j] in (None, 0) for j in range(i, n)) else []
        res, L = [], clue[k]
        for s in range(i, n - L + 1):
            if any(known[j] == 1 for j in range(i, s)): break          # skipped a known-filled cell
            if any(known[j] == 0 for j in range(s, s + L)): continue
            end = s + L
            if end < n:
                if known[end] == 1: continue
                for rest in go(end + 1, k + 1):
                    res.append((0,) * (s - i) + (1,) * L + (0,) + rest)
            else:
                for rest in go(end, k + 1):
                    res.append((0,) * (s - i) + (1,) * L + rest)
        return res
    return go(0, 0)

def line_solve(row_clues, col_clues):
    """Returns (grid with None for undetermined cells, number of deduction passes)."""
    H, W = len(row_clues), len(col_clues)
    g = [[None] * W for _ in range(H)]
    passes = 0
    while True:
        passes += 1; changed = False
        for lines, get, put in (
            (row_clues, lambda i: g[i], lambda i, j, v: g[i].__setitem__(j, v)),
            (col_clues, lambda j: [g[i][j] for i in range(H)], lambda j, i, v: g[i].__setitem__(j, v)),
        ):
            for idx, clue in enumerate(lines):
                cur = get(idx); opts = placements(clue, len(cur), tuple(cur))
                if not opts: raise ValueError("contradiction")
                for pos in range(len(cur)):
                    vals = {o[pos] for o in opts}
                    if cur[pos] is None and len(vals) == 1:
                        put(idx, pos, vals.pop()); changed = True
        if not changed: return g, passes

if __name__ == "__main__":
    out, ok_all = [], True
    for name, pic in PICTURES.items():
        sol = grid(pic)
        rc = [clues(r) for r in sol]; cc = [clues([r[j] for r in sol]) for j in range(len(sol[0]))]
        g, passes = line_solve(rc, cc)
        unknown = sum(v is None for r in g for v in r)
        ok = unknown == 0 and g == sol
        ok_all &= ok
        print(f"{name:11s} {len(sol[0])}x{len(sol)}  passes={passes:2d}  undetermined={unknown:2d}  "
              f"{'LOGIC-SOLVABLE (unique)' if ok else 'REJECT: needs guessing / not unique'}")
        if ok: out.append({"name": name, "rows": rc, "cols": cc, "solution": sol})
    json.dump(out, open("puzzles.json", "w"))
    print(f"\n{len(out)}/{len(PICTURES)} accepted -> puzzles.json")
