"""Even Beats: the page's patterns == euclid.py's for all 136 (k, n); presets give tresillo/cinquillo; the offline
recording of E(k, n) twice contains exactly 2k clicks for several cases and never clips; phone 0; no errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "euclid.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.evenApi !== undefined")
    js = pg.evaluate("""() => { const o = {}; for (let n = 1; n <= 16; n++) for (let k = 1; k <= n; k++)
        o[k + ',' + n] = evenApi.bjorklund(k, n).map(v => v ? 'x' : '.').join(''); return o; }""")
    check("all 136 patterns == Python", js == py, str([k for k in py if js.get(k) != py[k]][:4]))
    pg.click("[data-k='5'][data-n='8']"); check("cinquillo preset shows x.xx.xx.", pg.evaluate("window.even.pattern") == "x.xx.xx.")
    pg.click("[data-k='3'][data-n='8']"); check("tresillo preset shows x..x..x.", pg.evaluate("window.even.pattern") == "x..x..x.")
    bad = []
    for k, n in ((3, 8), (5, 8), (7, 12), (1, 4), (4, 4)):
        r = pg.evaluate(f"evenRender({k}, {n})")
        if r["onsets"] != 2 * k or not (0.05 < r["peak"] < 1): bad.append((k, n, r))
    check("recordings: exactly 2k clicks for two loops, audible, no clipping", not bad, str(bad))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
