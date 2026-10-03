"""Cross-implementation check: the page's JavaScript lineSolve() must reach EXACTLY the same
deductions (cell by cell, None/0/1) and the same pass count as the Python line_solve(), on all
real puzzles plus random pictures of many sizes and densities."""
import json, random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from puzzles import line_solve, clues

cases = [p["solution"] for p in json.load(open(D / "puzzles.json"))]
rng = random.Random(43)
for _ in range(300):
    w, h, dens = rng.randint(3, 15), rng.randint(3, 15), rng.choice([0.3, 0.5, 0.6, 0.75])
    cases.append([[1 if rng.random() < dens else 0 for _ in range(w)] for _ in range(h)])
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.goto((D / "make.html").as_uri())
    agree = solvable = 0
    for g in cases:
        rc = [clues(r) for r in g]; cc = [clues([r[j] for r in g]) for j in range(len(g[0]))]
        pyg, pyp = line_solve(rc, cc)
        js = pg.evaluate("([rc, cc]) => lineSolve(rc, cc)", [rc, cc])
        same = js["grid"] == pyg and js["passes"] == pyp
        agree += same; solvable += all(v is not None for r in pyg for v in r)
        if not same: print("DISAGREE on", len(g[0]), "x", len(g))
    ctx.close()
print(f"JS vs Python: {agree}/{len(cases)} identical (grids + pass counts); {solvable} of them logic-solvable")
print("XCHECK OK" if agree == len(cases) else "XCHECK FAILED")
