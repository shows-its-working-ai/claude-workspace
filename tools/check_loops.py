"""Stacked animation loops, site-wide (cycle 228, from cycle 227's Ring Your Bell bug: 3 presses of Start = 3 frame
loops, invisible to every other check because the drawing looked identical).
Wraps requestAnimationFrame to COUNT calls per second. First measures ONE loop's rate on a blank page (headless runs
~240/s, not 60), then on every page that uses requestAnimationFrame presses each visible button in <main> THREE times (a toggle: play, pause, play) and
measures again. More than 1.4 loops' worth after any triple press = a stacked loop.
It must SEE first: a planted page that starts a new loop on every click (never cancelling) must be flagged, or the
whole check fails as blind."""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
COUNT = "(() => { const raf = window.requestAnimationFrame.bind(window); window.__raf = 0; window.requestAnimationFrame = cb => { window.__raf++; return raf(cb); }; })();"
ONE = "data:text/html,<main><button id=b>go</button></main><script>(function f(){ requestAnimationFrame(f); })()</script>"
LEAKY = "data:text/html,<main><button id=b>go</button></main><script>document.getElementById('b').onclick = () => (function f(){ requestAnimationFrame(f); })();</script>"
files = sys.argv[1:] or sorted(f for f in subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.html"], cwd=ROOT,
        capture_output=True, text=True).stdout.split() if "requestAnimationFrame" in (ROOT / f).read_text(encoding="utf-8", errors="ignore") and "template" not in f)
def rate(pg, ms=700):
    pg.evaluate("window.__raf = 0"); pg.wait_for_timeout(ms); return pg.evaluate("window.__raf") * 1000 / ms
def worst_after_presses(pg):
    worst, label = rate(pg), "load"
    btns = pg.locator("main button")
    for i in range(btns.count()):
        b = btns.nth(i)
        try:
            if not b.is_visible() or b.is_disabled(): continue
            name = (b.inner_text() or b.get_attribute("aria-label") or "?").strip()[:30]
            b.click(timeout=1000); b.click(timeout=1000); b.click(timeout=1000)   # 3: play, pause, play exposes a pause that doesn't stop
        except Exception: continue
        r = rate(pg)
        if r > worst: worst, label = r, name
    return worst, label
bad = []
with sync_playwright() as p:
    ctx = open_browser(p); ctx.add_init_script(COUNT)
    pg = ctx.new_page(); pg.goto(ONE); pg.wait_for_timeout(300); one = rate(pg, 1000); pg.close()
    limit = 1.4 * one
    pg = ctx.new_page(); pg.goto(LEAKY); pg.wait_for_timeout(300); leak, _ = worst_after_presses(pg); pg.close()
    seen = leak > limit
    print(f"one loop = {one:.0f}/s; limit {limit:.0f}/s; control (a page that stacks a loop per click): {leak:.0f}/s {'SEEN' if seen else 'NOT SEEN'}")
    for f in files:
        pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto((ROOT / f).as_uri()); pg.wait_for_timeout(500)
        w, label = worst_after_presses(pg)
        ok = w <= limit
        print(f"{'ok  ' if ok else 'STACKED'} {f}: worst {w:.0f}/s after a triple press of '{label}'")
        if not ok: bad.append(f)
        pg.close()
    ctx.close()
print(f"{len(files)} animated pages checked; {len(bad)} with stacked loops")
print("LOOPS OK" if seen and not bad else ("LOOP CHECK BLIND" if not seen else "STACKED LOOPS FOUND"))
