"""Generator check. Every generated puzzle must be independently logic-solvable by the PYTHON solver
(not just the JS one that accepted it). Measure the acceptance rate of smoothed vs raw-noise candidates
(control), and the generation time."""
import sys, time
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from puzzles import line_solve, clues
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.goto((D / "make.html").as_uri())
    pg.add_script_tag(path=str(D / "generator.js"))
    ok = True; levels = {}; tries = []; t0 = time.time()
    for seed in range(1, 51):
        z = pg.evaluate(f"generatePuzzle({seed})")
        if z is None: print("seed", seed, "gave up"); ok = False; continue
        g = z["solution"]; rc = [clues(r) for r in g]; cc = [clues([r[j] for r in g]) for j in range(len(g[0]))]
        pyg, pyp = line_solve(rc, cc)
        good = pyg == g and pyp == z["passes"] and rc == z["rows"] and cc == z["cols"]; ok &= good
        levels[z["level"]] = levels.get(z["level"], 0) + 1; tries.append(z["tries"])
    dt = (time.time() - t0) / 50
    print(f"50 puzzles: all independently verified by the Python solver: {ok}; levels {levels}; "
          f"mean tries {sum(tries)/len(tries):.1f}; {dt*1000:.0f} ms per puzzle (incl. browser round-trips)")
    def acceptance(smooth):
        r = pg.evaluate(f"""(() => {{ let ok = 0, n = 0;
          for (let s = 1000; s < 1300; s++) {{ const g = _candidate(s, 10, 10, {smooth});
            const f = g.flat().reduce((a, b) => a + b, 0); if (f < 25 || f > 75) continue; n++;
            const rows = g.map(clues), cols = g[0].map((_, j) => clues(g.map(r => r[j])));
            if (!lineSolve(rows, cols).grid.flat().some(v => v === null)) ok++; }}
          return [ok, n]; }})()""")
        return r
    for sm in (0, 1, 2, 3):
        a, n = acceptance(sm); print(f"  smoothing passes {sm}: {a}/{n} candidates logic-solvable ({100*a/max(n,1):.0f}%)")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
