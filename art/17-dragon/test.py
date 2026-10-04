"""Paper Dragon: the page's creases == dragon.py's for n = 1..16; the page's corner counts (corners, touched twice,
more often) == an independent Python walk of dragon.json's creases; slider updates; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "dragon.json").read_text(encoding="utf-8"))
def walk(s):
    x = y = 0; dx, dy = 1, 0; v = {(0, 0): 1}
    for c in s + "E":
        x += dx; y += dy; v[(x, y)] = v.get((x, y), 0) + 1
        if c == "L": dx, dy = -dy, dx
        elif c == "R": dx, dy = dy, -dx
    return len(v), sum(n == 2 for n in v.values()), sum(n > 2 for n in v.values())
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.dragonApi !== undefined")
    js = pg.evaluate("() => { const o = {}; for (let n = 1; n <= 16; n++) o[n] = dragonApi.creases(n); return o; }")
    check("creases == Python for 1..16 folds", js == py)
    bad = []
    for n in (1, 3, 5, 9, 12, 16):
        pg.fill("#n", str(n)); d = pg.evaluate("window.dragon")
        if d["n"] != n or (d["corners"], d["twice"], d["more"]) != walk(py[str(n)]): bad.append((n, d["corners"], d["twice"], walk(py[str(n)])))
    check("slider: page's corner counts == Python walk (6 sizes)", not bad, str(bad))
    check("16 folds: 0 corners touched more than twice, shown in words", pg.evaluate("window.dragon.more") == 0 and "touched twice" in pg.inner_text("#facts") and "more often" not in pg.inner_text("#facts"))
    pg.fill("#n", "3"); check("3 folds lists all 7 creases", pg.inner_text("#creases").replace(" ", "") == py["3"])
    lit = pg.evaluate("""() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n; }""")
    check("the curve is drawn", lit > 2000, f"{lit} px")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.fill("#n", "12")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_dragon_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
