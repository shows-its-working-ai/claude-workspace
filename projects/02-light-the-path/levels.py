"""Level generator + brute-force verifier for "Light the Path".

A level: rule, width W (ring), steps T, an editable zone in row 0, goal cells
(must be 1) and avoid cells (must stay 0). Every level is generated from a
hidden solution, then the solver checks EVERY subset of the zone up to size 4:
  - the level is solvable,
  - par == the true minimum number of toggles,
  - the empty board does NOT already win,
  - at most MAX_SOLUTIONS minimal solutions (so it's a puzzle, not a lottery),
  - v2: EVERY mark is necessary (quality.audit: each eliminates >= 1 attempt
    of size <= par that all the other marks allow). v1 had 13/40 useless marks.

Chapter 1 is frozen in levels_ch1.json (8 levels, 31x18). Chapter 2 ("Gliders")
is generated here: Rule 110 on a bigger board. Geometry is per level.
"""
import itertools
import json
import random

MAX_SOLUTIONS = 3
CH2 = {"W": 41, "T": 28, "zone": list(range(13, 27))}      # 14 editable cells
CH2_PLAN = [(110, 2), (110, 3), (110, 3), (110, 4)]

def run(rule, toggles, W, T):
    row = [0] * W
    for x in toggles:
        row[x] ^= 1
    rows = [row]
    for _ in range(T - 1):
        r = rows[-1]
        rows.append([(rule >> (4 * r[x - 1] + 2 * r[x] + r[(x + 1) % W])) & 1 for x in range(W)])
    return rows

def grid(level, toggles):
    return run(level["rule"], toggles, level["W"], level["T"])

def wins(level, toggles):
    g = grid(level, toggles)
    return all(g[t][x] for t, x in level["goals"]) and not any(g[t][x] for t, x in level["avoid"])

def solve(level, max_k=4):
    for k in range(max_k + 1):
        sols = [c for c in itertools.combinations(level["zone"], k) if wins(level, c)]
        if sols:
            return k, sols
    return None, []

def make(rule, par, rng, geo):
    """v2: CONSTRUCT the marks. Greedily add the mark that kills the most
    still-winning wrong attempts (ties broken randomly), then prune any mark
    that kills nothing on its own, so every remaining mark is necessary."""
    from quality import audit
    W, T, zone = geo["W"], geo["T"], geo["zone"]
    attempts = [c for k in range(par + 1) for c in itertools.combinations(zone, k)]
    grids = {a: run(rule, a, W, T) for a in attempts}
    cells = [(t, x) for t in range(T // 2, T) for x in range(W)]
    for _ in range(500):
        hidden = tuple(sorted(rng.sample(zone, par)))
        g = grids[hidden]
        cand = [("goals" if g[t][x] else "avoid", (t, x)) for t, x in cells]
        ok = lambda a, m: grids[a][m[1][0]][m[1][1]] == (m[0] == "goals")
        marks, alive = [], [a for a in attempts if a != hidden]
        while alive and len(marks) < 6:
            rng.shuffle(cand)
            best = max(cand, key=lambda m: sum(not ok(a, m) for a in alive))
            if not any(not ok(a, best) for a in alive):
                break
            marks.append(best)
            alive = [a for a in alive if ok(a, best)]
        if len(alive) > MAX_SOLUTIONS - 1 or not any(m[0] == "goals" for m in marks):
            continue
        level = {"rule": rule, "par": par, "W": W, "T": T, "zone": zone,
                 "goals": [m[1] for m in marks if m[0] == "goals"],
                 "avoid": [m[1] for m in marks if m[0] == "avoid"]}
        while True:  # prune redundant marks
            gm = [("goal", m) for m in level["goals"]] + [("avoid", m) for m in level["avoid"]]
            elim = audit(level)[1]
            if min(elim) >= 1:
                break
            kind, cell = gm[elim.index(0)]
            level["goals" if kind == "goal" else "avoid"].remove(cell)
        k, sols = solve(level)
        if k == par and len(sols) <= MAX_SOLUTIONS and not wins(level, ()):
            level["solutions"] = [list(s) for s in sols]
            return level
    raise RuntimeError(f"no level for rule {rule} par {par}")

if __name__ == "__main__":
    ch1 = json.load(open("levels_ch1.json"))
    rng = random.Random(110)
    ch2 = [make(rule, par, rng, CH2) for rule, par in CH2_PLAN]
    levels = ch1 + ch2
    for i, lv in enumerate(levels, 1):
        # independent re-check of the stored answers, for EVERY level
        assert all(wins(lv, s) for s in lv["solutions"])
        assert solve(lv)[0] == lv["par"] and not wins(lv, ())
        print(f"level {i:2d}: rule {lv['rule']:3d} {lv['W']}x{lv['T']} par {lv['par']}  "
              f"minimal solutions {len(lv['solutions'])}  marks {len(lv['goals']) + len(lv['avoid'])}")
    json.dump(levels, open("levels.json", "w"))
