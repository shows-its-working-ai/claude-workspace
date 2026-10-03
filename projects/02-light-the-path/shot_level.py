"""Solves one level by clicks in Claude's own browser and screenshots it.
Usage: shot_level.py <level number, 1-based>"""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

n = int(sys.argv[1]); lv = json.load(open(D / "levels.json"))[n - 1]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.set_viewport_size({"width": 700, "height": 900})
    pg.goto((D / "index.html").as_uri()); pg.click(f"button.lv[data-i='{n - 1}']")
    b = pg.locator("#cv").bounding_box(); cw = b["width"] / lv["W"]; ch = b["height"] / lv["T"]
    for x in lv["solutions"][0]:
        pg.mouse.click(b["x"] + (x + .5) * cw, b["y"] + .5 * ch)
    pg.click("#run"); pg.wait_for_function("document.body.dataset.result !== undefined")
    print("result:", pg.evaluate("document.body.dataset.result"))
    pg.screenshot(path=str(D / f"l{n}.png"), full_page=True); ctx.close()
