"""Against: the page's merged rhythm == against.py's for all 144 (p, q); presets; an offline recording of two loops
has exactly 2 * (p + q - gcd) beats for pairs whose beats are >= 100 ms apart (closer ones blur into one click with
this detector, so they are not claimed); audible, no clipping; phone 0; no JS errors."""
import json, sys
from math import gcd
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "against.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.againstApi !== undefined")
    js = pg.evaluate("""() => { const o = {}; for (let p = 1; p <= 12; p++) for (let q = 1; q <= 12; q++)
        o[p + ',' + q] = againstApi.merged(p, q).on; return o; }""")
    check("all 144 merged rhythms == Python", js == py, str([k for k in py if js.get(k) != py[k]][:4]))
    pg.click("[data-p='4'][data-q='3']")
    check("4 against 3 preset: 6 beats at twelfths 0,3,4,6,8,9", pg.evaluate("window.against.merged") == [0, 3, 4, 6, 8, 9])
    check("facts line says 6 beats", "6 beats" in pg.inner_text("#facts"))
    bad = []
    for a, b in ((3, 2), (4, 3), (5, 4), (6, 4), (1, 1), (5, 3)):
        r = pg.evaluate(f"againstRender({a}, {b})")
        if r["onsets"] != 2 * (a + b - gcd(a, b)) or not (0.05 < r["peak"] < 1): bad.append((a, b, r))
    check("recordings: 2*(p+q-gcd) beats over two loops, audible, no clipping", not bad, str(bad))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.click("[data-p='5'][data-q='4']")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_against_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
