"""Keyboard-only checks for Confluence and Beat Rates (no mouse events sent)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

def tab_to(pg, test, limit=60):
    for _ in range(limit):
        if pg.evaluate(f"(el => !!el && ({test}))(document.activeElement)"): return True
        pg.keyboard.press("Tab")
    return False

def rendered(pg, n):
    pg.wait_for_function(f"document.body.dataset.rendered === '{n}'", timeout=60000)
    return int(pg.inner_text("#n"))

ok = True
with sync_playwright() as p:
    ctx = open_browser(p); errs = []
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_viewport_size({"width": 1000, "height": 700})
    pg.goto((ROOT / "art/02-confluence/index.html").as_uri()); rendered(pg, 0)
    ok &= tab_to(pg, "el.id === 'c'")
    cur = pg.evaluate("getComputedStyle(document.getElementById('cur')).display")
    pg.keyboard.press("Enter"); a = rendered(pg, 1)
    for _ in range(5): pg.keyboard.press("ArrowRight")
    pg.keyboard.press("v"); b = rendered(pg, 2)
    pg.keyboard.press("r")
    for k in ["ArrowDown"] * 6 + ["ArrowRight"] * 4: pg.keyboard.press(k)
    pg.keyboard.press("r"); c = rendered(pg, 3)
    kinds = pg.evaluate("[pts.map(p => p.vortex), rivers.length]")   # sink, vortex, then one river
    pg.keyboard.press("r"); pg.keyboard.press("ArrowUp"); pg.keyboard.press("Escape"); pg.keyboard.press("r")
    still = int(pg.inner_text("#n"))      # cancelled river + a lone R must not add anything
    pg.keyboard.press("r")                # close the river the lone R just opened (too short -> dropped)
    pg.keyboard.press("c"); d = rendered(pg, 0)
    pg.keyboard.press("Tab"); hidden = pg.evaluate("getComputedStyle(document.getElementById('cur')).display") == "none"
    conf = cur == "block" and (a, b, c, still, d) == (1, 2, 3, 3, 0) and hidden and kinds == [[False, True], 1]
    print(f"Confluence: cursor shown={cur}, counts after Enter/V/R..R/cancel/C = {(a, b, c, still, d)}, kinds={kinds}, cursor hidden on blur={hidden} -> {'ok' if conf else 'FAIL'}")
    ok &= conf

    pg2 = ctx.new_page(); pg2.on("pageerror", lambda e: errs.append(str(e)))
    pg2.goto((ROOT / "projects/03-beat-rates/index.html").as_uri())
    t = tab_to(pg2, "el.closest('#t') && el.tagName === 'BUTTON'"); pg2.keyboard.press("Enter")
    on = pg2.evaluate("!!document.querySelector('#t button.on')")
    pg2.keyboard.press("Enter")                                   # same button again stops it
    off = pg2.evaluate("!document.querySelector('#t button.on')")
    pr = tab_to(pg2, "el.classList.contains('ans')", 120); pg2.keyboard.press("Enter")
    # The answer pressed is whichever button Tab reaches first; it's right ~50% of the time.
    # What we test is that a keyboard answer REGISTERS (score x/1), not that the guess was right.
    scored = "/1" in pg2.inner_text("#pres")
    br = t and on and off and pr and scored
    print(f"Beat Rates: table play/stop by Enter = {on}/{off}, practice answer by keyboard scored = {scored} -> {'ok' if br else 'FAIL'}")
    ok &= br
    print("js errors:", errs); ok &= not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
