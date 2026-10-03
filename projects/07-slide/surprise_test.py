"""Slide "Surprise me" (cycle 70). Prediction (written first): every level the page generates passes the SAME
standard as the built-in 12 when re-checked independently in Python (quality.analyse): one shortest solution,
at least one trap, par 7-14; and a level made by clicking the button is solvable by keyboard in exactly par moves
using a solution Python finds (the page never computes or shows one)."""
import sys
from collections import deque
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from make_levels import slide, solve
from quality import analyse

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
KEY = {"U": "ArrowUp", "D": "ArrowDown", "L": "ArrowLeft", "R": "ArrowRight"}
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    gen = pg.evaluate("[...Array(30).keys()].map(i => slideGame.generate(1000 + i))")
    bad = []; tries = []
    for i, L in enumerate(gen):
        if L is None: bad.append((i, "none")); continue
        a = analyse(L); tries.append(L["tries"])
        if not (a["par"] == L["par"] and a["shortest_solutions"] == 1 and a["traps"] > 0 and 7 <= a["par"] <= 14):
            bad.append((i, a))
    check("30 generated levels all meet the standard (Python re-check)", not bad, f"bad={bad[:3]}; tries median {sorted(tries)[len(tries) // 2]}, max {max(tries)}")
    same = pg.evaluate("JSON.stringify(slideGame.generate(1234)) === JSON.stringify(slideGame.generate(1234))")
    check("same seed -> same level", same)
    for k in range(3):
        pg.click("#surprise"); L = pg.evaluate("slideGame.LEVELS[slideGame.LEVELS.length - 1]")
        par, path, _ = solve(L["grid"], tuple(L["start"]), tuple(L["goal"]))
        for d in path: pg.keyboard.press(KEY[d])
        st = pg.evaluate("slideGame.state()")
        check(f"button level {k + 1} ({L['name']}): keyboard solve in {st['moves']} = par {L['par']}", st["won"] and st["moves"] == L["par"] == par)
    check("no JS errors", not errs, f"{errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
