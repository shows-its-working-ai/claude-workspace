"""One Long Line: the page's Hilbert path for 32x32 == hilbert.py's; a REAL click on a cell lights exactly the cells
within k steps along the path (recomputed here from the Python path); Hilbert lights a compact box, row-by-row a
full-width stripe on the same cell; a REAL touchscreen tap at phone width picks the right cell; control: nothing lit
before any tap; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser, open_touch
from playwright.sync_api import sync_playwright
py = json.loads((D / "hilbert.json").read_text(encoding="utf-8"))
ns = {"__file__": str(D / "hilbert.py")}; exec((D / "hilbert.py").read_text(encoding="utf-8").split("res = {}")[0], ns)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def tap(pg, cx, cy, n, touch=False):
    pg.evaluate("document.getElementById('cv').scrollIntoView({block: 'center'})"); b = pg.locator("#cv").bounding_box()
    x, y = b["x"] + (cx + .5) / n * b["width"], b["y"] + (cy + .5) / n * b["height"]
    (pg.touchscreen.tap if touch else pg.mouse.click)(x, y)
def expected(n, cell, mode):
    path = [ns["d2xy"](n, d) for d in range(n * n)] if mode == "hil" else [(d % n, d // n) for d in range(n * n)]
    at = path.index(tuple(cell)); k = max(1, n * n >> 4)
    return sorted(map(list, path[max(0, at - k): at + k + 1]))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.line !== undefined")
    check("control: nothing lit before any tap", pg.evaluate("line.picked") is None and pg.evaluate("line.lit.length") == 0)
    js = pg.evaluate("[...Array(1024)].map((_, d) => lineApi.d2xy(32, d))")
    check("page Hilbert path for 32x32 == hilbert.py", js == py["order5"])
    pg.click("#orders button[data-o='4']"); tap(pg, 6, 9, 16)
    lit = sorted(pg.evaluate("line.lit")); check("real click on (6, 9): picks it", pg.evaluate("line.picked") == [6, 9])
    check("Hilbert: lit cells == the 33 within 16 steps (recomputed in Python)", lit == expected(16, (6, 9), "hil") and len(lit) == 33)
    hb = pg.evaluate("line.box")
    pg.click("#row"); rl = sorted(pg.evaluate("line.lit")); rb = pg.evaluate("line.box")
    check("row-by-row on the same cell: lit cells == Python's", rl == expected(16, (6, 9), "row"))
    check("Hilbert lights a compact box, row-by-row a full-width stripe", max(hb) < 16 and rb[0] == 16, f"Hilbert {hb}, rows {rb}")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 1000}); pg.click("#hil"); tap(pg, 6, 9, 16)
    pg.screenshot(path=str(D.parents[1] / "tools" / "_hilbert_look.png"), full_page=True)
    ctx.close()
    tc = open_touch(p); tp = tc.new_page(); tp.goto((D / "index.html").as_uri()); tp.wait_for_function("window.line !== undefined")
    tp.click("#orders button[data-o='5']"); tap(tp, 20, 3, 32, touch=True)
    check("real touchscreen tap at phone width on (20, 3) of 32x32", tp.evaluate("line.picked") == [20, 3] and sorted(tp.evaluate("line.lit")) == expected(32, (20, 3), "hil"))
    tc.close()
print("ALL PASS" if ok else "FAILURES")
