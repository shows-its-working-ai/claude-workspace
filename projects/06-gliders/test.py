"""The page measures each glider live; check those measurements against (a) the published catalogue and
(b) an INDEPENDENT Python measurement (the strict 3-period test from glider_search3.py's method)."""
import sys
from fractions import Fraction as Fr
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8); NT = 24; W = 14 * NT; OFF = 14 * 12; T = 400
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
CAT = {"A": Fr(2, 3), "B": Fr(-1, 2), "C": Fr(0), "E": Fr(-4, 15), "G": Fr(-1, 3)}
SEEDS = {"A": [0, 5], "B": [7, 14], "C": [6, 23], "E": [6], "G": [2, 18]}
def step(r): return TABLE[4 * np.roll(r, 1) + 2 * r + np.roll(r, -1)]
def py_measure(seed):
    base = np.tile(TILE, NT); row = base.copy(); row[[OFF + o for o in seed]] ^= 1; clean = base.copy(); hist = []
    for _ in range(T + 1): hist.append(row != clean); row = step(row); clean = step(clean)
    last = hist[T]
    for p in range(1, 121):
        for d in range(-W // 2, W // 2):
            if all(np.array_equal(np.roll(hist[T - (r + 1) * p], d), hist[T - r * p]) for r in range(3)):
                return Fr(d, p)
    return None
ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); js = pg.evaluate("window.gliderResults")
    for name in "ABCEG":
        r = js[name]; jsv = Fr(r["d"], r["p"]); pyv = py_measure(SEEDS[name])
        good = r["match"] and jsv == CAT[name] and pyv == CAT[name]; ok &= good
        print(f"{name}: page measured period {r['p']} shift {r['d']:+d} = {jsv} | Python {pyv} | catalogue {CAT[name]} -> {'ok' if good else 'FAIL'}")
    ticks = pg.locator(".ok").count(); print("check marks shown on the page:", ticks); ok &= ticks == 5
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth"); pg.screenshot(path=str(D / "look.png"), full_page=True)
    print("phone overflow:", ov, "| js errors:", errs); ok &= ov == 0 and not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
