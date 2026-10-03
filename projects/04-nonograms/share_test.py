"""Sharing: paint the Teacup in the maker, follow its link, solve it in the game by clicks -> win.
Then feed the game malformed/hostile hashes: each must be rejected politely, inject nothing,
throw no errors, and fall back to a normal puzzle."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
NEW = ["..#..#..", "..#..#..", "..#..#..", "........", "#######.", "#.....##", "#.....##", "######.."]
BAD = ["#c=<img src=x onerror=alert(1)>", "#c=1~1", "#c=99_1_1_1_1~1_1_1_1_1", "#c=", "#c=1.1.1.1.1.1_1_1_1_1~1_1_1_1_1",
       "#c=" + "1_" * 20 + "1~1_1_1_1_1", "#c=3_3_3_3_3~3_3_3_3_4", "#c=0_0_0_0_0~0_0_0_0_0"]
ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("dialog", lambda d: (errs.append("DIALOG " + d.message), d.dismiss()))
    pg.goto((D / "make.html").as_uri()); pg.select_option("#w", "8"); pg.select_option("#h", "8")
    for r, row in enumerate(NEW):
        for c, ch in enumerate(row):
            if ch == "#": pg.click(f'.cell[data-r="{r}"][data-c="{c}"]')
    pg.click("#check"); href = pg.get_attribute("#share", "href"); pg.click("#share")
    pg.wait_for_selector('#pick button.cur')
    name = pg.inner_text('#pick button.cur')
    for r, row in enumerate(NEW):
        for c, ch in enumerate(row):
            if ch == "#": pg.click(f'.cell[data-r="{r}"][data-c="{c}"]')
    won = pg.evaluate("document.body.dataset.won") == "1"
    print(f"share link: {href[:60]}... -> opened '{name.split()[0]} {name.split()[1]}', solved by clicks: {won}")
    ok &= won and "Shared picture" in name and "#c=" in href
    for h in BAD:
        q = ctx.new_page(); q.on("pageerror", lambda e: errs.append(str(e)))
        q.goto((D / "index.html").as_uri() + h)
        shared = "Shared picture" in q.inner_text("#pick")
        msg = q.inner_text("#msg"); injected = q.locator("img").count()
        good = not shared and "couldn't be read" in msg and injected == 0 and q.locator(".cell").count() > 0
        ok &= good; print(f"  hostile/malformed {h[:34]:34s} -> rejected={not shared} fallback_ok={q.locator('.cell').count() > 0} injected={injected} -> {'ok' if good else 'FAIL'}")
        q.close()
    print("js errors / dialogs:", errs); ok &= not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
