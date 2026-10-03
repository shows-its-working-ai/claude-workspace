"""A/B render for Confluence in Claude's own browser (dark mode):
A = 2 sinks + 1 vortex (cycle 13), B = 1 dragged river + the same vortex."""
import math, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

def vortex(pg):
    pg.keyboard.down("Shift"); pg.mouse.click(640, 250); pg.keyboard.up("Shift")

with sync_playwright() as p:
    ctx = open_browser(p); errs = []
    for name in ("A", "B"):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.set_viewport_size({"width": 1280, "height": 800}); pg.emulate_media(color_scheme="dark")
        pg.goto((D / "index.html").as_uri())
        pg.wait_for_function("document.body.dataset.rendered === '0'", timeout=30000)
        if name == "A":
            pg.mouse.click(420, 330); pg.mouse.click(860, 520)
        else:  # an S-curve river across the frame
            pts = [(150 + i * 10, 450 + 150 * math.sin(i / 14)) for i in range(100)]
            pg.mouse.move(*pts[0]); pg.mouse.down()
            for x, y in pts[1:]: pg.mouse.move(x, y)
            pg.mouse.up()
        vortex(pg)
        want = "3" if name == "A" else "2"
        pg.wait_for_function(f"document.body.dataset.rendered === '{want}'", timeout=120000)
        print(name, "placed:", pg.inner_text("#n"))
        pg.screenshot(path=str(D / f"ab_{name}.png")); pg.close()
    print("errors:", errs); ctx.close()
