"""Clicks a few points into Confluence in Claude's own browser and screenshots it."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = open_browser(p); errs = []
    for scheme in ("dark", "light"):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.set_viewport_size({"width": 1280, "height": 800}); pg.emulate_media(color_scheme=scheme)
        pg.goto((D / "index.html").as_uri())
        pg.wait_for_function("document.body.dataset.rendered === '0'", timeout=30000)
        if scheme == "dark":
            pg.screenshot(path=str(D / "empty.png"))
        pg.mouse.click(420, 330); pg.mouse.click(860, 520)
        pg.keyboard.down("Shift"); pg.mouse.click(640, 250); pg.keyboard.up("Shift")
        pg.wait_for_function("document.body.dataset.rendered === '3'", timeout=60000)
        print(scheme, "placed:", pg.inner_text("#n"))
        pg.screenshot(path=str(D / f"three_{scheme}.png")); pg.close()
    print("errors:", errs); ctx.close()
