"""Gear Drawing: for every ring/wheel choice on the page, its stated trips and bumps == r/g and R/g; the page's curve
formula == spiro.py's at many points; for a few gear pairs, the bumps the page states == local maxima of the radius
counted from the page's own points; the curve really closes after the stated trips and not before; phone 0."""
import sys
from math import gcd, hypot, pi
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {}; exec((D / "spiro.py").read_text(encoding="utf-8").split("bad, N = [], 0")[0], ns)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.spiroApi !== undefined")
    Rs = pg.evaluate("[...document.querySelectorAll('#R option')].map(o => +o.value)"); rs = pg.evaluate("[...document.querySelectorAll('#r option')].map(o => +o.value)")
    wrong = []
    for R in Rs:
        for r in rs:
            pg.select_option("#R", str(R)); pg.select_option("#r", str(r)); s = pg.evaluate("window.spiro"); g = gcd(R, r)
            if (s["trips"], s["lobes"]) != (r // g, R // g) or f"{r // g} time" not in pg.inner_text("#facts"): wrong.append((R, r))
    check(f"stated trips and bumps == r/g and R/g for all {len(Rs) * len(rs)} gear pairs", not wrong, str(wrong[:3]))
    diff = pg.evaluate("ts => ts.map(([R, r, d, t]) => spiroApi.pt(R, r, d, t))", [[96, 60, 39, 0.37 * k] for k in range(50)])
    check("page curve == spiro.py's formula", all(abs(a - b) < 1e-9 for (x, y), k in zip(diff, range(50)) for a, b in zip((x, y), ns["pt"](96, 60, 39, 0.37 * k))))
    for R, r in ((96, 60), (105, 63), (120, 64)):
        g = gcd(R, r); trips = r // g; d = 0.65 * r; S = 3000 * trips
        rad = pg.evaluate(f"[...Array({S})].map((_, i) => Math.hypot(...spiroApi.pt({R}, {r}, {d}, 2 * Math.PI * {trips} * i / {S})))")
        mid = (max(rad) + min(rad)) / 2; lob = sum(1 for i in range(S) if rad[i] > rad[i - 1] and rad[i] >= rad[(i + 1) % S] and rad[i] > mid)
        ends = [hypot(*(a - b for a, b in zip(ns["pt"](R, r, d, 2 * pi * m), ns["pt"](R, r, d, 0)))) for m in range(1, trips + 1)]
        check(f"R={R} r={r}: {lob} bumps counted from the page's points == stated {R // g}; closes first at trip {trips}",
              lob == R // g and ends[-1] < 1e-6 and all(e > 1e-6 for e in ends[:-1]))
    pg.click("#slow"); pg.wait_for_timeout(300)
    check("'Draw it slowly' animates without errors", not errs)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.select_option("#R", "105"); pg.select_option("#r", "63")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_spiro_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
