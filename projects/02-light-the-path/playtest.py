"""Plays every level in Claude's own browser by real mouse clicks."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
levels = json.load(open(HERE / "levels.json"))
ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((HERE / "index.html").as_uri())
    pg.evaluate("localStorage.clear()")
    for i, lv in enumerate(levels):
        for attempt, cells in (("empty", []), ("solution", lv["solutions"][0])):
            pg.click(f"button.lv[data-i='{i}']")
            box = pg.locator("#cv").bounding_box()
            cw = box["width"] / lv["W"]; ch = box["height"] / lv["T"]
            for x in cells:
                pg.mouse.click(box["x"] + (x + .5) * cw, box["y"] + .5 * ch)
            pg.click("#run")
            pg.wait_for_function("document.body.dataset.result !== undefined", timeout=10000)
            res = pg.evaluate("document.body.dataset.result")
            want = "lose" if attempt == "empty" else "win"
            flag = "ok" if res == want else "FAIL"; ok &= res == want
            print(f"level {i+1} {attempt:8s} -> {res:4s} [{flag}]")
    done = pg.evaluate("document.querySelectorAll('button.lv.done').length")
    print("levels marked solved:", done, "/", len(levels))
    pg.click("button.lv[data-i='6']")
    pg.screenshot(path=str(HERE / "shot.png"), full_page=True)
    pg.set_viewport_size({"width": 390, "height": 800})
    print("phone overflow px:", pg.evaluate("document.documentElement.scrollWidth - innerWidth"))
    print("js errors:", errs)
    ctx.close()
print("ALL PASS" if ok and done == len(levels) and not errs else "FAILURES")
