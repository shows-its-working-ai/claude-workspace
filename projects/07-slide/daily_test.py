"""Slide "Today's level" (cycle 97). Prediction (written first, about my own code): for 365 consecutive dates every
daily level meets the standard (re-checked independently in Python) and no two days give the same level.
Also: the same date always gives the same level; the button loads today's UTC level, named with the date, and
pressing it twice doesn't add a second copy; solvable by keyboard in exactly par."""
import datetime, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from make_levels import solve
from quality import analyse
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
KEY = {"U": "ArrowUp", "D": "ArrowDown", "L": "ArrowLeft", "R": "ArrowRight"}
dates = [(datetime.date(2026, 1, 1) + datetime.timedelta(days=i)).isoformat() for i in range(365)]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    levels = pg.evaluate("ds => ds.map(d => slideGame.dailyFor(d))", dates)
    missing = [d for d, L in zip(dates, levels) if L is None]
    check("a level exists for all 365 days", not missing, f"{missing[:3]}")
    bad = []
    for d, L in zip(dates, levels):
        if L is None: continue
        a = analyse(L)
        if not (a["par"] == L["par"] and a["shortest_solutions"] == 1 and a["traps"] > 0 and 7 <= a["par"] <= 14): bad.append(d)
    check("every daily level meets the standard (Python re-check)", not bad, f"{bad[:3]}")
    keys = {(tuple(L["grid"]), tuple(L["start"]), tuple(L["goal"])) for L in levels if L}
    check("no two days give the same level", len(keys) == len([L for L in levels if L]), f"{len(keys)} distinct of 365")
    check("same date -> same level", pg.evaluate("JSON.stringify(slideGame.dailyFor('2026-10-03')) === JSON.stringify(slideGame.dailyFor('2026-10-03'))"))
    today = pg.evaluate("new Date().toISOString().slice(0, 10)")
    n0 = pg.evaluate("slideGame.LEVELS.length"); pg.click("#daily"); pg.click("#daily"); n1 = pg.evaluate("slideGame.LEVELS.length")
    L = pg.evaluate("slideGame.LEVELS[slideGame.LEVELS.length - 1]")
    check("button loads today's level once (named with the UTC date)", n1 == n0 + 1 and L["name"] == f"Daily {today}", f"{L['name']}, {n0}->{n1}")
    par, path, _ = solve(L["grid"], tuple(L["start"]), tuple(L["goal"]))
    for d in path: pg.keyboard.press(KEY[d])
    st = pg.evaluate("slideGame.state()")
    check("today's level solved by keyboard in exactly par", st["won"] and st["moves"] == L["par"] == par, f"{st['moves']} vs {L['par']}")
    check("no JS errors", not errs, f"{errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
