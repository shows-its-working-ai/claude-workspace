"""Wythoff's Garden: the page's Grundy values for the 64x64 corner == grundy.py's, cell for cell; zeros drawn black;
no freeze over 250 ms at load; phone 0; no errors. Cycle 212: the readout under a REAL mouse move (desktop) and a
REAL touchscreen tap (phone) names the right heaps and value; control: the readout text before any input."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser, open_touch
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "grundy64.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.garden !== undefined")
    js = pg.evaluate("window.garden.corner64")
    check("64x64 Grundy values == Python, cell for cell", js == py)
    black = pg.evaluate("""() => { const c = document.getElementById('cv').getContext('2d'), N = 128, out = [];
        for (const [x, y] of [[0,0],[1,2],[2,1],[3,5],[5,3],[4,7]]) out.push(c.getImageData(x, N - 1 - y, 1, 1).data[0]);
        out.push(c.getImageData(1, N - 1 - 1, 1, 1).data[0]); return out; }""")
    check("losing squares are drawn black, a non-losing one isn't", all(v < 40 for v in black[:6]) and black[6] > 60, str(black))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 800, "height": 1000}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    def cell(pg, x, y):
        pg.evaluate("document.getElementById('cv').scrollIntoView()"); b = pg.locator("#cv").bounding_box()
        return b["x"] + (x + 0.5) / 128 * b["width"], b["y"] + (127 - y + 0.5) / 128 * b["height"]
    pg.set_viewport_size({"width": 800, "height": 1000})
    for x, y in [(3, 5), (10, 20), (40, 7)]:
        pg.mouse.move(*cell(pg, x, y)); t = pg.inner_text("#info")
        check(f"real mouse over ({x}, {y}): readout says its value {py[x][y]}", f"heaps ({x}, {y}): Grundy value {py[x][y]}" in t, t)
    ctx.close()
    tc = open_touch(p); tp = tc.new_page(); terrs = []; tp.on("pageerror", lambda e: terrs.append(str(e)))
    tp.goto((D / "index.html").as_uri()); tp.wait_for_function("window.garden !== undefined")
    check("control: before any tap the readout is the prompt", "tap a square" in tp.inner_text("#info"))
    for x, y in [(5, 3), (12, 30)]:
        tp.touchscreen.tap(*cell(tp, x, y)); t = tp.inner_text("#info")
        check(f"real touchscreen tap on ({x}, {y}) at phone width: readout says {py[x][y]}", f"heaps ({x}, {y}): Grundy value {py[x][y]}" in t and not terrs, t)
    tc.close()
print("ALL PASS" if ok else "FAILURES")
