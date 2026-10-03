"""Drives the picture maker by clicks: the ORIGINAL rejected Teacup must be flagged with exactly 14
undecided squares (stuck.py's count in cycle 38); the fixed Teacup must pass as easy, 3 passes."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
OLD = ["........", "...#.#..", "..#.#...", "........", "#######.", "#.....##", "#.....##", ".#####.."]
NEW = ["..#..#..", "..#..#..", "..#..#..", "........", "#######.", "#.....##", "#.....##", "######.."]
ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "make.html").as_uri())
    for name, pic, want in (("old Teacup", OLD, ("no", "14")), ("fixed Teacup", NEW, ("ok", "0"))):
        pg.select_option("#w", "8"); pg.select_option("#h", "8")
        for r, row in enumerate(pic):
            for c, ch in enumerate(row):
                if ch == "#": pg.click(f'.cell[data-r="{r}"][data-c="{c}"]')
        pg.click("#check")
        got = (pg.evaluate("document.body.dataset.verdict"), pg.evaluate("document.body.dataset.unknown"))
        outlined = pg.locator(".cell.q").count()
        text = pg.inner_text("#verdict")
        good = got == want and outlined == int(want[1]); ok &= good
        print(f"{name}: verdict={got[0]} undecided={got[1]} outlined={outlined} | {text} -> {'ok' if good else 'FAIL'}")
        if name == "fixed Teacup": ok &= "3 passes (easy)" in text
    pg.select_option("#w", "15"); pg.select_option("#h", "15")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    print("phone overflow at 15x15:", ov, "| js errors:", errs); ok &= ov == 0 and not errs
    g2 = ctx.new_page(); g2.goto((D / "index.html").as_uri())
    g2.click("text=Make your own picture"); linked = g2.url.endswith("make.html")
    print("linked from the game page:", linked); ok &= linked
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
