"""Plays every nonogram in Claude's own browser.
Mouse: fill the solution cell by cell -> not won until the last cell, won after; an extra wrong
cell breaks the win; crossing empty cells does not. Keyboard: solve one puzzle with arrows + Space."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

puzzles = json.load(open(D / "puzzles.json")); ok = True
cell = lambda r, c: f'.cell[data-r="{r}"][data-c="{c}"]'
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_viewport_size({"width": 900, "height": 1000})
    pg.goto((D / "index.html").as_uri())
    for i, pz in enumerate(puzzles):
        pg.click(f'#pick button[data-i="{i}"]')
        filled = [(r, c) for r, row in enumerate(pz["solution"]) for c, v in enumerate(row) if v]
        empty = [(r, c) for r, row in enumerate(pz["solution"]) for c, v in enumerate(row) if not v]
        for r, c in filled[:-1]: pg.click(cell(r, c))
        early = pg.evaluate("document.body.dataset.won")
        pg.click(cell(*filled[-1]))
        won = pg.evaluate("document.body.dataset.won"); msg = pg.inner_text("#msg")
        pg.click(cell(*empty[0])); broken = pg.evaluate("document.body.dataset.won")
        pg.click(cell(*empty[0]))                                    # toggle it back off
        for r, c in empty[:3]: pg.click(cell(r, c), button="right")  # crosses must not matter
        still = pg.evaluate("document.body.dataset.won")
        good = early == "0" and won == "1" and "Solved" in msg and broken == "0" and still == "1"
        ok &= good
        print(f"{pz['name']:11s} not-won-early={early=='0'} won={won=='1'} wrong-cell-breaks={broken=='0'} crosses-ok={still=='1'} -> {'ok' if good else 'FAIL'}")
    # keyboard-only solve of the first puzzle
    pg.click('#pick button[data-i="0"]'); pz = puzzles[0]
    pg.focus(cell(0, 0)); r = c = 0
    for tr, row in enumerate(pz["solution"]):
        for tc, v in enumerate(row):
            if not v: continue
            while r < tr: pg.keyboard.press("ArrowDown"); r += 1
            while r > tr: pg.keyboard.press("ArrowUp"); r -= 1
            while c < tc: pg.keyboard.press("ArrowRight"); c += 1
            while c > tc: pg.keyboard.press("ArrowLeft"); c -= 1
            pg.keyboard.press("Space")
    kb = pg.evaluate("document.body.dataset.won") == "1"
    print("keyboard-only solve of", pz["name"], "->", "ok" if kb else "FAIL"); ok &= kb
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.screenshot(path=str(D / "look.png"), full_page=True)
    print("phone overflow:", ov, "| js errors:", errs); ok &= ov == 0 and not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
