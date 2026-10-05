"""Kissing Circles: the page's curvatures up to 100 == apollo.py's (169); every page circle up to 1,000 is tangent to
its three parents in the page's own drawing coordinates; tapping a circle's centre picks THAT circle and the caption's
arithmetic is right; control: tapping outside every inner circle picks none; phone 0; no JS errors."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "apollo.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.kiss !== undefined")
    ks = pg.evaluate("kissApi.gasket(100).map(e => e.c[0]).sort((a, b) => a - b)")
    check("page curvatures up to 100 == apollo.py (169)", ks == py["curvatures_le_100"] and len(ks) == 169)
    worst = pg.evaluate("""() => { let w = 0, n = 0; for (const e of kissApi.gasket(1000)){ if (!e.parents) continue; const a = kissApi.P(e.c);
        for (const q of e.parents){ const b = kissApi.P(q), d = Math.hypot(a.x - b.x, a.y - b.y), want = q[0] < 0 ? b.r - a.r : a.r + b.r;
          w = Math.max(w, Math.abs(d - want)); n++; } } return [w, n]; }""")
    check("every circle up to 1,000 touches its 3 parents on the canvas (pixels)", worst[0] < 1e-6, f"worst={worst[0]:.2e} over {worst[1]} contacts")
    pg.click("[data-k='100']")
    for k in (6, 23, 35):
        c = pg.evaluate(f"(() => {{ const e = kissApi.gasket(100).find(e => e.c[0] === {k}); return kissApi.P(e.c); }})()")
        pg.evaluate(f"kissApi.pick({c['x']}, {c['y']})"); cap = pg.inner_text("#cap")
        m = re.search(r"Curvature (\d+), made from (-?\d+), (-?\d+), (-?\d+): 2 × \(.*\) − (\d+|\(-\d+\)) = (\d+)", cap)
        good = m and int(m[1]) == k == int(m[6]) and 2 * (int(m[2]) + int(m[3]) + int(m[4])) - int(m[5].strip("()")) == k
        check(f"tap the centre of a {k}: picks it, caption arithmetic right", good and pg.evaluate("kiss.picked[0]") == k, cap)
    pg.evaluate("kissApi.pick(2, 2)")
    check("control: tapping the corner (outside every circle) picks nothing", pg.evaluate("kiss.picked") is None)
    pg.click("[data-k='1000']"); check("1,000 button draws more circles", pg.evaluate("kiss.count") > 169, str(pg.evaluate("kiss.count")))
    pg.set_viewport_size({"width": 390, "height": 800})
    pg.click("[data-k='100']")
    pg.evaluate("document.getElementById('cv').scrollIntoView({block: 'start'})"); box = pg.locator("#cv").bounding_box()
    c = pg.evaluate("kissApi.gasket(100).filter(e => e.c[0] === 11).map(e => kissApi.P(e.c)).sort((a, b) => a.y - b.y)[0]")
    pg.mouse.click(box["x"] + c["x"] * box["width"] / 720, box["y"] + c["y"] * box["height"] / 720)
    check("a real mouse click on an 11 at phone width (canvas shown at half size) picks the 11", pg.evaluate("kiss.picked && kiss.picked[0]") == 11, f"canvas shown at {box['width']:.0f}px")
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.click("[data-k='100']")
    c = pg.evaluate("(() => { const e = kissApi.gasket(100).find(e => e.c[0] === 23); return kissApi.P(e.c); })()"); pg.evaluate(f"kissApi.pick({c['x']}, {c['y']})")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_kiss_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
