"""Pendulum Wave checks, in Claude's own browser.
Prediction (written first): at t = 60/n the 15 phases fall into exactly n groups, for n = 1..6, and the
page's numbers agree with an independent Python computation using exact fractions.
Also: lengths are physically right (T = 2*pi*sqrt(L/g)), the jump buttons land where they say, no JS errors,
no phone overflow, and the animation actually advances when playing (and stops when paused)."""
import math, sys
from fractions import Fraction as Fr
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")

# independent: exact fractional phase of pendulum k at time t (t a Fraction)
py_phase = lambda k, t: (Fr(51 + k, 60) * t) % 1
for n in range(1, 7):
    groups = {py_phase(k, Fr(60, n)) for k in range(15)}
    check(f"python: t=60/{n} -> {n} groups", len(groups) == n, f"(got {len(groups)})")

with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_timeout(300)
    for n in range(1, 7):
        ph = pg.evaluate(f"[...Array(15).keys()].map(k => pw.phaseAt(k, 60/{n}))")
        groups = sorted({round(x, 6) % 1 for x in ph})
        pyg = sorted({round(float(py_phase(k, Fr(60, n))), 6) for k in range(15)})
        check(f"page: t=60/{n} -> {n} groups, same as Python", len(groups) == n and groups == pyg, f"{groups}")
    # physics: L = g / (2 pi f)^2 for f = 51/60 .. 65/60 Hz
    for k in (0, 14):
        L = pg.evaluate(f"pw.lengthCm({k})"); want = 100 * 9.81 / (2 * math.pi * (51 + k) / 60) ** 2
        T = 2 * math.pi * math.sqrt(L / 100 / 9.81)
        check(f"length k={k}: {L:.2f} cm gives period {T:.4f} s = 60/{51+k}", abs(L - want) < 1e-9 and abs(T - 60 / (51 + k)) < 1e-9)
    # jump buttons land where they say
    for label, t in (("20 s", 20), ("30 s", 30)):
        pg.locator(".jumps button", has_text=label).click(); pg.wait_for_timeout(100)
        clock = pg.inner_text("#clock"); check(f"jump '{label}' shows {clock}", clock == f"{t:.1f} s")
    # paused stays put; playing advances
    c1 = pg.inner_text("#clock"); pg.wait_for_timeout(500); c2 = pg.inner_text("#clock")
    check("paused: clock frozen", c1 == c2, f"{c1} -> {c2}")
    pg.click("#play"); pg.wait_for_timeout(1200); c3 = pg.inner_text("#clock")
    adv = float(c3.split()[0]) - float(c2.split()[0])
    check("playing: clock advances ~1 s", 0.7 < adv < 1.5, f"{c2} -> {c3}")
    pg.click("#play")
    pg.screenshot(path=str(D / "look.png"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    # reduced motion: must start paused
    pg2 = ctx.new_page(); pg2.emulate_media(reduced_motion="reduce"); pg2.goto((D / "index.html").as_uri())
    pg2.wait_for_timeout(700)
    check("reduced motion: starts paused", pg2.inner_text("#play") == "Play" and pg2.inner_text("#clock") == "0.0 s")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
