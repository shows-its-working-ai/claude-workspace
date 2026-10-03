"""Renders the self-portrait (light + dark), shows a hover and a keyboard-focus tooltip, checks phone width."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    ctx = open_browser(p); errs = []
    for scheme in ("light", "dark"):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.set_viewport_size({"width": 1000, "height": 760}); pg.emulate_media(color_scheme=scheme)
        pg.goto((D / "index.html").as_uri())
        cell = pg.locator(".cell").nth(24); b = cell.bounding_box()
        pg.mouse.move(b["x"] + 10, b["y"] + 20)
        pg.screenshot(path=str(D / f"look_{scheme}.png")); pg.close()
    pg = ctx.new_page(); pg.set_viewport_size({"width": 390, "height": 800}); pg.goto((D / "index.html").as_uri())
    pg.keyboard.press("Tab"); pg.keyboard.press("Tab")
    focus_tip = pg.evaluate("getComputedStyle(document.getElementById('tip')).display")
    print("phone overflow:", pg.evaluate("document.documentElement.scrollWidth - innerWidth"),
          "| tooltip on keyboard focus:", focus_tip, "| errors:", errs)
    ctx.close()
