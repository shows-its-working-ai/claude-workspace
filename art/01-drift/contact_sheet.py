"""Renders each seed at a REAL window size (1280x800, dark), then tiles the
screenshots. Rendering inside small iframes is unfair: Drift scales to the window."""
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

seeds = (D / "tastetest_seeds.txt").read_text().split()
(D / "tt").mkdir(exist_ok=True)
with sync_playwright() as p:
    ctx = open_browser(p)
    pg = ctx.new_page()
    pg.set_viewport_size({"width": 1280, "height": 800})
    pg.emulate_media(color_scheme="dark")
    for s in seeds:
        pg.goto((D / "index.html").as_uri() + "#" + s)
        pg.wait_for_timeout(1200)
        pg.screenshot(path=str(D / "tt" / f"{s}.png"))
    cells = "".join(f'<figure><img src="tt/{s}.png"><figcaption>{i + 1}</figcaption></figure>'
                    for i, s in enumerate(seeds))
    (D / "contact.html").write_text(
        "<!doctype html><meta charset=utf-8><style>body{margin:0;background:#000;display:grid;"
        "grid-template-columns:repeat(5,1fr);gap:6px;padding:6px}figure{margin:0;position:relative}"
        "img{width:100%;display:block}figcaption{position:absolute;top:4px;left:6px;color:#fff;"
        "font:bold 14px sans-serif;text-shadow:0 0 3px #000}</style>" + cells)
    pg.set_viewport_size({"width": 1600, "height": 1000})
    pg.goto((D / "contact.html").as_uri())
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(D / "contact.png"), full_page=True)
    ctx.close()
print("ok", len(seeds))
