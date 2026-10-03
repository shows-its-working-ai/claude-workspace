"""Defect view check: for each ether level, solve by clicks; the number of highlighted cells
must equal Python's count of cells differing from the clean ether. Screenshots level 15."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from levels import grid, circular_span

levels = json.load(open(D / "levels.json")); ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_viewport_size({"width": 700, "height": 1000})
    pg.goto((D / "index.html").as_uri())
    for i, lv in enumerate(levels):
        if "base" not in lv:
            continue
        sol = lv["solutions"][0]
        want = sum(a != b for r1, r2 in zip(grid(lv, sol), grid(lv, ())) for a, b in zip(r1, r2))
        pg.click(f"button.lv[data-i='{i}']")
        b = pg.locator("#cv").bounding_box()
        for x in sol:
            pg.mouse.click(b["x"] + (x + .5) * b["width"] / lv["W"], b["y"] + .5 * b["height"] / lv["T"])
        pg.click("#run"); pg.wait_for_function("document.body.dataset.result !== undefined")
        got = int(pg.evaluate("document.body.dataset.changed"))
        last = [x for x, (a, c) in enumerate(zip(grid(lv, sol)[-1], grid(lv, ())[-1])) if a != c]
        span = circular_span(last, lv["W"]) if last else 0
        good = got == want and pg.evaluate("document.body.dataset.result") == "win" and 0 < span <= 30; ok &= good
        print(f"level {i+1}: highlighted {got}, python diff {want}, final-row defect span {span} -> {'ok' if good else 'FAIL'}")
        if i == len(levels) - 1:
            pg.screenshot(path=str(D / "diff15.png"))
    pg.click("button.lv[data-i='0']")
    hidden = pg.evaluate("getComputedStyle(document.getElementById('diffwrap')).display") == "none"
    print("switch hidden on non-ether level:", hidden, "| js errors:", errs); ok &= hidden and not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
