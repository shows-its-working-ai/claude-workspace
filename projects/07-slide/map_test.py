"""Slide map (cycle 72). Prediction (written first): for every level, the map the page draws after a win has
exactly the resting spots, slides and traps an independent Python search finds, and its green route is par long.
Also: the button is hidden until the level is won, hides again on a new level, and toggles."""
import json, sys
from collections import deque
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from make_levels import slide
from quality import analyse
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
KEY = {"U": "ArrowUp", "D": "ArrowDown", "L": "ArrowLeft", "R": "ArrowRight"}
levels = json.loads((D / "levels.json").read_text(encoding="utf-8"))
def py_counts(L):
    start = tuple(L["start"]); seen = {start}; q = deque([start]); edges = 0
    while q:
        p = q.popleft()
        for d in "UDLR":
            n = slide(L["grid"], *p, d)
            if n == p: continue
            edges += 1
            if n not in seen: seen.add(n); q.append(n)
    a = analyse(L); return len(seen), edges, a["traps"], a["par"]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    for i, L in enumerate(levels):
        pg.click(f'#pick button[data-i="{i}"]')
        hidden_before = pg.locator("#showmap").is_hidden()
        for d in L["solution"]: pg.keyboard.press(KEY[d])
        pg.click("#showmap")
        got = pg.evaluate("(c => [+c.dataset.spots, +c.dataset.edges, +c.dataset.traps, +c.dataset.route])(document.getElementById('map'))")
        want = list(py_counts(L))
        check(f"{L['name']}: map spots/slides/traps/route {got} == Python {want}; hidden before win", got == want and hidden_before)
    # cycle 72 bug: the map was drawn UNDER the tiles; data matched but nothing showed. Check pixels too.
    shown = pg.locator("#board").screenshot()
    pg.click("#showmap"); check("toggle hides the map", pg.evaluate("document.getElementById('map').style.display") == "none")
    hidden = pg.locator("#board").screenshot(); check("the map visibly changes the board's pixels", shown != hidden)
    pg.click('#pick button[data-i="0"]'); check("new level hides the button again", pg.locator("#showmap").is_hidden())
    check("no JS errors", not errs, f"{errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
