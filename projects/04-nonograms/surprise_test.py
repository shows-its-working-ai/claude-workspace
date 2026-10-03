"""'Surprise me' in the real game: press it 5 times; each time read the clues the PAGE is showing,
solve them with the Python solver, click the answer in, and expect a win."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from puzzles import line_solve
ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_viewport_size({"width": 900, "height": 1100})
    pg.goto((D / "index.html").as_uri())
    for k in range(5):
        pg.click("#surprise")
        cur = pg.inner_text("#pick button.cur")
        z = pg.evaluate("({rows: P[0].rows, cols: P[0].cols, kept: 'solution' in P[0]})")
        g, _ = line_solve(z["rows"], z["cols"])
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v: pg.click(f'.cell[data-r="{r}"][data-c="{c}"]')
        won = pg.evaluate("document.body.dataset.won") == "1"
        good = won and "Surprise" in cur and not z["kept"]; ok &= good
        print(f"  {' '.join(cur.split()[:2])} ({cur.split()[-1]}): solved by clicks={won}, answer kept in page={z['kept']} -> {'ok' if good else 'FAIL'}")
    print("js errors:", errs); ok &= not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
