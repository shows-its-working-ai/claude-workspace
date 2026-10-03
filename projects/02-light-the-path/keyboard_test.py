"""Plays every level with the KEYBOARD ONLY (Tab / Shift+Tab / Enter / Space).
Page state is only read to know where focus is; no mouse events are sent."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

levels = json.load(open(D / "levels.json"))

def focus_to(pg, js_test, limit=120):
    """Tab forward, then backward, until js_test(document.activeElement) is true."""
    for key in ("Tab", "Shift+Tab"):
        for _ in range(limit):
            if pg.evaluate(f"(el => !!el && ({js_test}))(document.activeElement)"):
                return True
            pg.keyboard.press(key)
    return False

ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.set_viewport_size({"width": 900, "height": 1000})
    pg.goto((D / "index.html").as_uri())
    for i, lv in enumerate(levels):
        good = focus_to(pg, f"el.matches(\"button.lv[data-i='{i}']\")")
        pg.keyboard.press("Enter")
        kept = pg.evaluate(f"document.activeElement.matches(\"button.lv[data-i='{i}']\")")
        for x in lv["solutions"][0]:
            good &= focus_to(pg, f"el.matches(\"#cells button[data-x='{x}']\")")
            if i == 0:
                visible = pg.evaluate("document.getElementById('cells').getBoundingClientRect().width > 50")
                print("  keyboard toolbar visible when focused:", visible); good &= visible
            pg.keyboard.press("Space")
        good &= focus_to(pg, "el.id === 'run'")
        pg.keyboard.press("Enter")
        pg.wait_for_function("document.body.dataset.result !== undefined", timeout=15000)
        res = pg.evaluate("document.body.dataset.result")
        good &= res == "win" and kept
        ok &= good
        print(f"level {i+1:2d}: focus kept after Enter={kept} result={res} -> {'ok' if good else 'FAIL'}")
    hidden = pg.evaluate("document.activeElement.id === 'run' && document.getElementById('cells').getBoundingClientRect().width <= 1")
    live = pg.evaluate("document.getElementById('msg').getAttribute('aria-live')")
    print("toolbar hidden again when focus leaves:", hidden, "| msg aria-live:", live, "| js errors:", errs)
    ok &= hidden and live == "polite" and not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
