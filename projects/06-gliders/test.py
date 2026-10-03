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
CAT = {"A": Fr(2, 3), "B": Fr(-1, 2), "C": Fr(0), "Ē": Fr(-8, 30), "G": Fr(-1, 3)}
CAT_PERIOD = {"Ē": 30}   # cycle 64: E (period 15) and Ē (period 30) share a speed
SEEDS = {"A": [0, 5], "B": [7, 14], "C": [6, 23], "Ē": [6], "G": [2, 18]}
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
    for name in ["A", "B", "C", "Ē", "G"]:
        r = js[name]; jsv = Fr(r["d"], r["p"]); pyv = py_measure(SEEDS[name])
        good = r["match"] and jsv == CAT[name] and pyv == CAT[name] and r["p"] == CAT_PERIOD.get(name, r["p"]); ok &= good
        print(f"{name.replace(chr(274), 'Ebar')}: page measured period {r['p']} shift {r['d']:+d} = {jsv} | Python {pyv} | catalogue {CAT[name]} -> {'ok' if good else 'FAIL'}")
    # cycle 57: the live E-speed ladder must match e_family.py's result (cycle 56): (30,-8) at 20..60 cells
    lad = js_l = pg.evaluate("window.ladder")
    want = [20, 28, 36, 44, 52, 60]
    lg = bool(lad) and [r["cells"] for r in lad] == want and all(r["p"] == 30 and r["d"] == -8 for r in lad)
    print("live ladder:", [(r["cells"], r["p"], r["d"]) for r in lad] if lad else None, "->", "ok" if lg else "FAIL"); ok &= lg
    ticks = pg.locator(".ok").count(); print("check marks shown on the page:", ticks); ok &= ticks == 5
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth"); pg.screenshot(path=str(D / "look.png"), full_page=True)
    print("phone overflow:", ov, "| js errors:", errs); ok &= ov == 0 and not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
