"""Moiré: the band spacing is MEASURED from the pixels the page drew, not taken from its formula. The canvas is read
back, blurred with a box twice the line spacing (the fine lines vanish), sampled along the mean line direction (the
direction in which the bands repeat), and the repeat distance is the first autocorrelation peak. It must be within
10% of 8 / (2 sin(theta/2)) at 4, 6 and 10 degrees (prediction, written before building). The slider set by keyboard
and a REAL drag both turn the sheet; phone width; no JS errors. Control: at 0 degrees there are no bands (the blurred
profile is flat), so the measurement isn't finding a period that's always there."""
import math, sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
PIX = "() => { const c = document.getElementById('cv'); return Array.from(c.getContext('2d').getImageData(0, 0, c.width, c.height).data.filter((_, i) => i % 4 === 0)); }"
def profile(pg, deg):
    img = np.array(pg.evaluate(PIX), dtype=float).reshape(800, 800) / 255
    k = 16; c = np.cumsum(np.cumsum(np.pad(img, ((1, 0), (1, 0))), 0), 1)   # box blur, 16 x 16, via an integral image
    blur = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / k / k
    h = math.radians(deg) / 2; u = (-math.sin(h), math.cos(h))   # mean line direction (x, y); bands repeat along it
    t = np.arange(-330, 330); cx = cy = blur.shape[0] / 2
    xs = np.clip((cx + t * u[0]).astype(int), 0, blur.shape[1] - 1); ys = np.clip((cy + t * u[1]).astype(int), 0, blur.shape[0] - 1)
    return blur[ys, xs]
def period(p):
    p = p - p.mean(); ac = np.correlate(p, p, "full")[len(p) - 1:]; ac /= ac[0]
    lag = next(i for i in range(1, len(ac)) if ac[i] < 0)   # past the first trough, then the highest peak
    return lag + int(np.argmax(ac[lag:len(p) // 2]))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.moire !== undefined")
    for deg in (4, 6, 10):
        pg.evaluate(f"() => {{ const s = document.getElementById('ang'); s.value = {deg * 10}; s.dispatchEvent(new Event('input')); }}")
        want = 8 / (2 * math.sin(math.radians(deg) / 2)); got = period(profile(pg, deg))
        check(f"{deg} degrees: measured bands {got} px vs formula {want:.1f} (within 10%)", abs(got - want) / want < 0.10, f"{abs(got - want) / want:.1%} off")
    pg.evaluate("() => { const s = document.getElementById('ang'); s.value = 0; s.dispatchEvent(new Event('input')); }")
    flat = profile(pg, 0).std(); banded = None
    pg.evaluate("() => { const s = document.getElementById('ang'); s.value = 60; s.dispatchEvent(new Event('input')); }"); banded = profile(pg, 6).std()
    check("control: at 0 degrees the blurred picture has no bands (flat), at 6 it does", flat < 0.02 and banded > 0.05, f"spread {flat:.3f} vs {banded:.3f}  {'SEEN' if flat < 0.02 < 0.05 < banded else 'NOT SEEN'}")
    pg.focus("#ang"); pg.keyboard.press("End")
    check("slider by keyboard: End turns it to 30 degrees", pg.evaluate("moire.deg") == 30 and "30.0" in pg.inner_text("#deg"))
    pg.keyboard.press("Home"); box = pg.locator("#cv").bounding_box()
    pg.mouse.move(box["x"] + 50, box["y"] + 200); pg.mouse.down(); pg.mouse.move(box["x"] + 50 + box["width"] / 3, box["y"] + 200, steps=8); pg.mouse.up()
    check("a real drag a third of the way across turns it about 10 degrees", 9 <= pg.evaluate("moire.deg") <= 11, pg.evaluate("moire.deg"))
    pg.set_viewport_size({"width": 390, "height": 800})
    check("phone width: no sideways scroll", pg.evaluate("document.documentElement.scrollWidth - innerWidth") == 0)
    check("no JS errors", not errs, errs)
    ctx.close()
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)
