"""Cycle 91: every multi-colour ant rule with 2-4 colours (strings over {L,R}, excluding all-L/all-R, which just
spin in place): 2 + 6 + 14 = 22 rules. Each runs 50,000 steps from an empty grid.
Prediction (written first): besides RL (and its mirror LR), at least 3 rules build a HIGHWAY within 50,000 steps.
Highway = the turn sequence becomes periodic with some period p <= 2,000 for the last 6,000 steps AND the ant has
moved (net displacement per period != 0); onset = first step of that periodicity (walking back).
Also recorded: exact mirror-symmetric moments with >= 100 cells (as in cycle 88), and the final cell count.
Writes survey.json for the gallery page."""
import itertools, json
from pathlib import Path
D = Path(__file__).resolve().parent
STEPS, WIN, PMAX = 50_000, 6_000, 2_000

def run(rule):
    x = y = 0; d = 0; n = len(rule); g = {}; turns = bytearray(); pos = []; sym = 0
    for t in range(1, STEPS + 1):
        c = g.get((x, y), 0); r = rule[c] == "R"
        d = (d + (1 if r else -1)) % 4; turns.append(r)
        c2 = (c + 1) % n
        if c2: g[(x, y)] = c2
        else: g.pop((x, y), None)
        x += (0, 1, 0, -1)[d]; y += (-1, 0, 1, 0)[d]; pos.append((x, y))
        if t % 500 == 0 and len(g) >= 100:                 # sample symmetry every 500 steps (cheap survey)
            xs = [p[0] for p in g]; ys = [p[1] for p in g]; sx = min(xs) + max(xs); sy = min(ys) + max(ys)
            if all(g.get((sx - a, b)) == v for (a, b), v in g.items()) or all(g.get((a, sy - b)) == v for (a, b), v in g.items()):
                sym += 1
    e = STEPS - WIN; tail = bytes(turns)
    for p in range(1, PMAX + 1):
        if tail[e - p:STEPS - p] == tail[e:STEPS]:
            dx = pos[-1][0] - pos[-1 - p][0]; dy = pos[-1][1] - pos[-1 - p][1]
            if (dx, dy) == (0, 0): continue
            t = e - p
            while t > 0 and turns[t - 1] == turns[t - 1 + p]: t -= 1
            return {"rule": rule, "highway": True, "period": p, "onset": t, "move": [dx, dy], "cells": len(g), "sym_samples": sym}
    return {"rule": rule, "highway": False, "cells": len(g), "sym_samples": sym}

if __name__ == "__main__":
    rules = ["".join(c) for n in (2, 3, 4) for c in itertools.product("LR", repeat=n) if len(set(c)) == 2]
    out = []
    for r in rules:
        res = run(r); out.append(res)
        print(r.ljust(5), "HIGHWAY period %d onset %d" % (res["period"], res["onset"]) if res["highway"] else "no highway",
              f"| cells {res['cells']} | symmetric samples {res['sym_samples']}", flush=True)
    (D / "survey.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    others = [r["rule"] for r in out if r["highway"] and r["rule"] not in ("RL", "LR")]
    # cycle 91 honesty: mirror pairs (swap L/R) behave identically, and LRLR is RL with its colours doubled.
    distinct = sorted({min(r, r.translate(str.maketrans("LR", "RL"))) for r in others} - {"LRLR"})
    print("genuinely new highway behaviours (one per mirror pair, minus LRLR = RL doubled):", distinct)
    print(f"{len(rules)} rules; highways besides RL/LR: {others}")
    print(f"PREDICTION (>= 3): as worded {'HELD' if len(others) >= 3 else 'FAILED'} ({len(others)} rule strings); "
          f"counting distinct behaviours {'HELD' if len(distinct) >= 3 else 'FAILED'} ({len(distinct)})")
    print("SURVEY DONE")
