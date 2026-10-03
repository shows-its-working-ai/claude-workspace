"""Pendulum Wave sound check (cycle 61).
Prediction (written first): the page's offline render of 2 s of audio correlates > 0.98 with an INDEPENDENT Python
synthesis (crossing times from exact fractions, same envelope), and a control with every note shifted by 20 ms
correlates < 0.5, so the high score can only come from the notes being at the right times.
Also: the page's crossing list equals Python's exactly (count and times), and the Sound button toggles."""
import sys
from fractions import Fraction as Fr
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")

RATE, T0, DUR = 22050, 30, 2
SCALE = [0, 2, 4, 7, 9]
def pitch(k): return 261.63 * 2 ** ((SCALE[k % 5] + 12 * (k // 5)) / 12)
def py_crossings(t0, t1):
    ev = []
    for k in range(15):
        f = Fr(51 + k, 60); j = 0
        while True:
            tc = (Fr(j, 2) + Fr(1, 4)) / f
            if tc > t1: break
            if tc > t0: ev.append((tc, k))
            j += 1
    return sorted(ev)
def synth(events, shift=0.0, gain=0.06, attack=0.005, length=0.3):
    out = np.zeros(int(RATE * DUR)); n = np.arange(len(out)) / RATE
    for tc, k in events:
        w = float(tc - T0) + shift
        if not (0 <= w < DUR): continue
        m = (n >= w) & (n < w + length); tt = n[m] - w
        env = np.where(tt < attack, gain * tt / attack, gain * (0.0001 / gain) ** ((tt - attack) / (length - attack)))
        out[m] += env * np.sin(2 * np.pi * pitch(k) * tt)
    return out

ev = py_crossings(T0, T0 + DUR)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_timeout(300)
    js = pg.evaluate(f"pw.crossings({T0}, {T0 + DUR}).map(e => [e.t, e.k])")
    same = len(js) == len(ev) and all(abs(a[0] - float(b[0])) < 1e-9 and a[1] == b[1] for a, b in zip(js, ev))
    check("page crossings == Python exact crossings", same, f"({len(js)} vs {len(ev)} notes in {DUR} s)")
    page = np.array(pg.evaluate(f"pwRender({T0}, {DUR}, {RATE})"))
    good = synth(ev); bad = synth(ev, shift=0.020)
    c_good = float(np.corrcoef(page, good)[0, 1]); c_bad = float(np.corrcoef(page, bad)[0, 1])
    check("render matches independent synthesis (> 0.98)", c_good > 0.98, f"r = {c_good:.4f}")
    check("control: notes shifted 20 ms do NOT match (< 0.5)", c_bad < 0.5, f"r = {c_bad:.4f}")
    check("render isn't silent and doesn't clip", 0.01 < np.abs(page).max() < 1.0, f"peak {np.abs(page).max():.3f}")
    b = pg.locator("#sound")
    t0 = (b.inner_text(), b.get_attribute("aria-pressed")); b.click(); t1 = (b.inner_text(), b.get_attribute("aria-pressed"))
    b.click(); t2 = (b.inner_text(), b.get_attribute("aria-pressed"))
    check("Sound button toggles off -> on -> off", t0 == ("Sound off", "false") and t1 == ("Sound on", "true") and t2 == t0, f"{t0} {t1} {t2}")
    # live path: Sound on + playing for ~2 s from t=10 must schedule about as many notes as the math says
    pg.evaluate("pwSetTime(10)"); b.click(); pg.click("#play"); pg.wait_for_timeout(2000); pg.click("#play"); b.click()
    played = pg.evaluate("pw.played"); t_end = float(pg.inner_text("#clock").split()[0])
    expect = len(py_crossings(10, t_end + 0.1))
    check("live playback schedules the expected notes", abs(played - expect) <= 4, f"played {played}, math says ~{expect} for 10 -> {t_end:.1f} s")
    check("no JS errors", not errs, f"{errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
