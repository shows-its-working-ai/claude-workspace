"""Endless Staircase: renders the page's own audio offline (2.25 cycles) and analyses it with FFTs:
(a) the spectrum one cycle later matches (periodic); (b) an eighth of a cycle later the whole log-spectrum has shifted
UP by 1/8 octave (and DOWN when the direction is reversed); (c) the loudness-weighted mean log-pitch stays within a
quarter octave; (d) audible, never clips; the page states it can't hear it; phone 0; no JS errors."""
import sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
RATE, T = 22050, 8.0
def logspec(x, t):                                                     # log-frequency magnitude spectrum around time t
    n = 16384; i = int(t * RATE); seg = x[i:i + n] * np.hanning(n)
    mag = np.abs(np.fft.rfft(seg)); f = np.fft.rfftfreq(n, 1 / RATE)
    grid = np.linspace(np.log2(40), np.log2(5000), 1200)               # 1200 bins over ~7 octaves
    return grid, np.interp(grid, np.log2(f[1:]), mag[1:])
def shift(a, b, grid):                                                 # octave shift s that best maps a onto b
    step = grid[1] - grid[0]; best = max(range(-60, 61), key=lambda k: np.dot(np.roll(a, k)[70:-70], b[70:-70]))
    return best * step
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.shepardRender !== undefined")
    up = np.array(pg.evaluate(f"shepardRender({2.25 * T}, 1)"), dtype=float)
    dn = np.array(pg.evaluate(f"shepardRender({1.25 * T}, -1)"), dtype=float)
    g, a0 = logspec(up, 1.0); _, a1 = logspec(up, 1.0 + T)
    corr = np.corrcoef(a0, a1)[0, 1]
    check("one cycle later the spectrum is the same (correlation > 0.95)", corr > 0.95, f"{corr:.3f}")
    _, b = logspec(up, 1.0 + T / 8); s_up = shift(a0, b, g)
    _, c0 = logspec(dn, 1.0); _, c1 = logspec(dn, 1.0 + T / 8); s_dn = shift(c0, c1, g)
    check("an eighth of a cycle later it has moved UP 1/8 octave", abs(s_up - 0.125) < 0.02, f"{s_up:+.3f} oct")
    check("...and DOWN 1/8 octave when reversed", abs(s_dn + 0.125) < 0.02, f"{s_dn:+.3f} oct")
    cents = []
    for k in range(17):
        gg, m = logspec(up, 0.5 + k * T / 8); w = m ** 2; cents.append(float((gg * w).sum() / w.sum()))
    check("weighted mean log-pitch stays within 1/4 octave over 2 cycles", max(cents) - min(cents) < 0.25, f"range {max(cents) - min(cents):.3f}")
    peak = float(np.abs(up).max()); rms = float(np.sqrt((up ** 2).mean()))
    check("audible and never clips", 0.02 < rms and peak < 1.0, f"rms {rms:.3f} peak {peak:.3f}")
    check("the page says it can't hear it", "can't hear" in pg.inner_text("main"))
    pg.click("#play"); pg.wait_for_timeout(600); pg.click("#dir"); pg.wait_for_timeout(600); pg.click("#play")    # live schedule is 10 minutes long
    check("play / direction / stop work", pg.inner_text("#dir") == "Going down" and pg.inner_text("#play") == "Play")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
