"""Puzzle-quality audit: for each mark (goal/avoid), how many attempts of
size <= par does it ELIMINATE that every other mark would allow? 0 = useless mark."""
import itertools, json
from levels import run, ZONE

def attempts(par):
    return [c for k in range(par + 1) for c in itertools.combinations(ZONE, k)]

def mark_ok(g, mark):
    kind, (t, x) = mark
    return g[t][x] == (1 if kind == "goal" else 0)

def audit(lv):
    marks = [("goal", tuple(m)) for m in lv["goals"]] + [("avoid", tuple(m)) for m in lv["avoid"]]
    grids = [run(lv["rule"], a) for a in attempts(lv["par"])]
    elim = []
    for i, m in enumerate(marks):
        others = marks[:i] + marks[i + 1:]
        elim.append(sum(1 for g in grids if all(mark_ok(g, o) for o in others) and not mark_ok(g, m)))
    return marks, elim

if __name__ == "__main__":
    import sys
    levels = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "levels.json"))
    useless = total = 0
    for i, lv in enumerate(levels, 1):
        marks, elim = audit(lv)
        useless += sum(e == 0 for e in elim); total += len(elim)
        print(f"level {i} rule {lv['rule']:3d}: eliminations per mark {elim}")
    print(f"USELESS MARKS: {useless} / {total}")
