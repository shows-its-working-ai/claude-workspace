"""Lights Out page (cycle 99). Prediction (written first, about my code): for all 12 levels the browser's own GF(2)
solver gives the same par as Python, and clicking Python's shortest solution turns every light off in exactly par.
Also: the page's solver equals Python's on 500 random boards (same set of 4 solutions, or none); no solutions shipped;
Surprise me boards are solvable; phone overflow 0; no JS errors."""
import json, random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from lights import solve
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
levels = json.loads((D / "levels.json").read_text(encoding="utf-8"))
check("no solutions shipped", '"solution"' not in (D / "index.html").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    rnd = random.Random(99); boards = [rnd.randrange(1 << 25) for _ in range(500)]
    js = pg.evaluate("bs => bs.map(b => lights.solveAll(b))", boards)
    mism = [b for b, s in zip(boards, js) if sorted(s) != sorted(solve(b))]
    check("page solver == Python solver on 500 random boards", not mism, f"{len(mism)} mismatches; {sum(1 for s in js if s)} solvable")
    for i, L in enumerate(levels):
        pg.click(f'#pick button[data-i="{i}"]')
        live = pg.evaluate(f"lights.LEVELS[{i}].livePar")
        for k in range(25):
            if L["solution"] >> k & 1: pg.click(f'.cell[data-i="{k}"]')
        st = pg.evaluate("lights.state()")
        check(f"{L['name']}: par {L['par']} == browser {live}; clicking the solution -> all off in {st['presses']}",
              live == L["par"] and st["board"] == 0 and st["presses"] == L["par"])
    pg.click("#surprise"); s = pg.evaluate("lights.LEVELS[lights.LEVELS.length - 1]")
    check("Surprise me board is solvable, par computed", s["par"] is not None and len(solve(s["board"])) == 4)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth"); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
