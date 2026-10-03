"""Checks Beat Rates in Claude's own browser: table vs Python, and table vs the
beat rate MEASURED from the rendered audio."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from beats import beat as pybeat

CASES = [(53, "M3"), (57, "M3"), (60, "M3"), (62, "m3"), (60, "M6"), (60, "P5"), (53, "P5"), (60, "P4")]
ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    for lo, iv in CASES:
        table = pg.evaluate(f"beatRate({lo}, '{iv}')")
        heard = pg.evaluate(f"measureBeat({lo}, '{iv}')")
        py = pybeat(lo, iv)
        err = abs(heard - table) / table
        good = abs(table - py) < 1e-9 and err < 0.08
        ok &= good
        print(f"lo={lo} {iv}: table {table:6.3f}  python {py:6.3f}  measured-from-audio {heard:6.3f}  ({err:5.1%}) {'ok' if good else 'FAIL'}")
    rows = pg.evaluate("document.querySelectorAll('#t tr').length - 1")
    pg.set_viewport_size({"width": 390, "height": 800})
    body_overflow = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    print("rows:", rows, "| page overflow at 390px:", body_overflow, "| js errors:", errs)
    ctx.close()
print("ALL PASS" if ok and rows == 13 and body_overflow == 0 and not errs else "FAILURES")
