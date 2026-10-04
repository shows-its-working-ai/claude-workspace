"""Window (cycle 134 adds sound): the rain sound renders audibly without clipping (6 s offline), the sound toggle
starts off and flips its label and aria-pressed, the picture still draws, no JS errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri() + "#4242"); pg.wait_for_timeout(500)
    r = pg.evaluate("windowRender()")
    check("rain sound: audible and never clipping", 0.02 < r["rms"] and r["peak"] < 1, f"rms={r['rms']:.3f} peak={r['peak']:.3f}")
    b = pg.locator("#sound")
    check("sound starts off", b.inner_text() == "sound: off" and b.get_attribute("aria-pressed") == "false")
    b.click(); on = (b.inner_text(), b.get_attribute("aria-pressed")); b.click(); off = (b.inner_text(), b.get_attribute("aria-pressed"))
    check("toggle: on then off, label and aria-pressed follow", on == ("sound: on", "true") and off == ("sound: off", "false"))
    check("no JS errors", not errs, str(errs))
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
