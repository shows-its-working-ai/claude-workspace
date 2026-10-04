"""Two-Colour Tiles: for random tilings, every tile piece on the page (the two caps and the band) is painted the colour
that truchet.py's region model + parity gives it, read back from the canvas pixels; neighbours across every arc
differ; tapping a square turns exactly that square; phone 0; no JS errors."""
import random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {}; exec((D / "truchet.py").read_text(encoding="utf-8").split("rng = random.Random")[0], ns)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.truchetApi !== undefined")
    A, B = pg.evaluate("['--a', '--b'].map(v => getComputedStyle(document.documentElement).getPropertyValue(v).trim())")
    hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    rng = random.Random(1881); wrong = arcs_same = 0
    for trial in range(5):
        n = rng.choice([6, 9, 12]); t = [[rng.randint(0, 1) for _ in range(n)] for _ in range(n)]
        pg.evaluate("t => truchetApi.set(t)", t)
        f, seps = ns["regions"](t, n, n)
        par = {}
        for r in range(n):
            for c in range(n):
                for k in range(4): y, x = ns["vertex"](r, c, k); par[f((r, c, k))] = (y + x) % 2
        arcs_same += sum(par[a] == par[b] for a, b in seps)
        s = 800 / n; pts = []
        for r in range(n):
            for c in range(n):
                caps = [(0.12, 0.12, 0), (0.88, 0.88, 2)] if t[r][c] == 0 else [(0.88, 0.12, 1), (0.12, 0.88, 3)]
                for fx, fy, k in caps: pts.append(((c + fx) * s, (r + fy) * s, par[f((r, c, k))]))
                mid = 1 if t[r][c] == 0 else 0
                pts.append(((c + 0.5) * s, (r + 0.5) * s, par[f((r, c, mid))]))      # tile centre lies in the band
        got = pg.evaluate("""ps => { const d = document.getElementById('cv').getContext('2d');
            return ps.map(([x, y]) => Array.from(d.getImageData(Math.floor(x), Math.floor(y), 1, 1).data.slice(0, 3))); }""", [[x, y] for x, y, _ in pts])
        for (x, y, pp), rgb in zip(pts, got):
            if tuple(rgb) != hexrgb(B if pp else A): wrong += 1
    check("every cap and band painted its region's parity colour (5 tilings, pixels read back)", wrong == 0, f"{wrong} wrong")
    check("no arc has the same colour on both sides (model)", arcs_same == 0)
    pg.evaluate("truchetApi.set([[0,0,0],[0,0,0],[0,0,0]])")
    box = pg.locator("#cv").bounding_box(); pg.mouse.click(box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.5)
    check("tapping the middle square turns exactly it", pg.evaluate("window.truchet.tiles") == [[0, 0, 0], [0, 1, 0], [0, 0, 0]])
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.click("#again")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_truchet_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
