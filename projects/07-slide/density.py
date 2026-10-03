"""How rocky should the ice be? (cycle 71)
Prediction (written first): the fraction of random 9x9 grids that make a GOOD level (goal reachable, par 7-14,
ONE shortest solution, >= 1 trap, >= 18 resting spots: the page's own standard) peaks at a middle rock density,
somewhere in 12-24%, falling off on both sides.
20,000 random grids (random start + goal) per density, fixed seeds."""
import json, random
from pathlib import Path
from quality import analyse
D = Path(__file__).resolve().parent
def grid(rng, dens):
    g = ["".join("#" if rng.random() < dens else "." for _ in range(9)) for _ in range(9)]
    free = [(r, c) for r in range(9) for c in range(9) if g[r][c] == "."]
    if len(free) < 2: return None
    s, t = rng.sample(free, 2); return {"grid": g, "start": list(s), "goal": list(t)}
rows = []
for pct in range(4, 41, 2):
    rng = random.Random(1000 + pct); n = 20000; reach = good = 0; pars = []
    for _ in range(n):
        L = grid(rng, pct / 100)
        if not L: continue
        try: a = analyse(L)
        except KeyError: continue                                 # goal unreachable (no dist entry)
        reach += 1; pars.append(a["par"])
        good += (7 <= a["par"] <= 14 and a["shortest_solutions"] == 1 and a["traps"] > 0 and a["spots"] >= 18)
    rows.append({"density": pct, "reachable": reach / n, "good": good / n, "mean_par": sum(pars) / max(1, len(pars))})
    print(f"{pct:2d}% rock: goal reachable {reach / n:5.1%}, GOOD {good / n:5.1%}, mean par {rows[-1]['mean_par']:.1f}")
best = max(rows, key=lambda r: r["good"]); print("peak GOOD at", best["density"], "%")
(D / "density.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
