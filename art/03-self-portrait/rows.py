"""How many rows does the strip take at desktop width? (the timeline should read as one line)"""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    c = open_browser(p); g = c.new_page(); g.set_viewport_size({"width": 1000, "height": 760})
    g.goto((D / "index.html").as_uri())
    n = g.locator(".cell").count()
    ys = {round(g.locator(".cell").nth(i).bounding_box()["y"]) for i in range(n)}
    print(f"{n} cells on {len(ys)} row(s) at 1000px"); c.close()
