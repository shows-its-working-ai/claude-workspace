"""Ant Golf, tested in Claude's own browser.
Prediction (written first): for all 8 holes, the browser's own exhaustive par equals the generator's, and painting
the generator's example solution by CLICKS wins. Also: Run with nothing painted misses (par >= 2 means 0 can't win);
no solutions shipped; Clear works; phone overflow 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
levels = json.loads((D / "levels.json").read_text(encoding="utf-8"))
html = (D / "index.html").read_text(encoding="utf-8")
check("no solutions shipped", '"example"' not in html and "solutions_at_par" not in html)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_viewport_size({"width": 800, "height": 1100})
    pg.goto((D / "index.html").as_uri())
    for i, L in enumerate(levels):
        pg.click(f'#pick button[data-i="{i}"]')
        live = pg.evaluate(f"golf.LEVELS[{i}].livePar")
        pg.click("#run"); empty_won = pg.evaluate("golf.state().won")
        pg.click("#clear")
        for x, y in L["example"]: pg.click(f'.c[data-x="{x}"][data-y="{y}"]')
        pg.click("#run"); st = pg.evaluate("golf.state()")
        check(f"{L['name']}: par {L['par']} == browser {live}; empty misses; example ({len(L['example'])} clicks) wins",
              live == L["par"] and not empty_won and st["won"] and len(st["painted"]) == L["par"])
    pg.click("#clear"); check("Clear empties the board", pg.evaluate("golf.state().painted") == [])
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
