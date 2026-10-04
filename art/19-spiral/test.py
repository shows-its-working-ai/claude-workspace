"""Prime Spiral: the page's spiral positions == spiral.py's for the first 5,000 cells; its primes up to 40,000 ==
4,203 (spiral.py); starting at 41, all 40 of Euler's values are prime on the page AND lie on one diagonal in the
page's own coordinates; with Euler shown, exactly those 40 pixels are red; buttons; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {}; exec((D / "spiral.py").read_text(encoding="utf-8").split("vals = [")[0], ns)
py = json.loads((D / "spiral.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.spiralApi !== undefined")
    jsp = pg.evaluate("[...Array(5000)].map((_, k) => spiralApi.pos(k))")
    check("spiral positions == Python (5,000 cells)", [tuple(t) for t in jsp] == ns["positions"](5000))
    check("primes 1..40,000 on the page == 4,203", pg.evaluate("window.spiral.lit") == py["primes_to_40000"] == 4203)
    pg.click("#from41"); pg.click("#euler")
    pts = pg.evaluate("spiralApi.EULER.map(v => spiralApi.pos(v - 41))")
    check("Euler's 40 are prime on the page", pg.evaluate("spiralApi.EULER.every(spiralApi.isPrime)") and pg.evaluate("spiralApi.EULER") == py["euler"])
    (x0, y0), (x1, y1) = pts[0], pts[1]; dx, dy = x1 - x0, y1 - y0
    check("...and lie on one diagonal in the page's coordinates", abs(dx) == abs(dy) != 0 and all((x - x0) * dy == (y - y0) * dx for x, y in pts))
    red = pg.evaluate("""() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, 200, 200).data;
        const hot = getComputedStyle(document.documentElement).getPropertyValue('--hot').trim(), h = [1, 3, 5].map(i => parseInt(hot.slice(i, i + 2), 16));
        let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] === h[0] && d[i + 1] === h[1] && d[i + 2] === h[2] && d[i + 3]) n++; return n; }""")
    check("with Euler shown, exactly 40 red pixels", red == 40, f"{red}")
    check("caption says they're on one diagonal", "on one diagonal" in pg.inner_text("#cap"))
    pg.click("#from1"); check("back to 1: caption suggests starting at 41", "start at 41" in pg.inner_text("#cap") and pg.evaluate("window.spiral.start") == 1)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.click("#from41")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_spiral_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
