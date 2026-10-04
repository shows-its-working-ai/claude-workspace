"""Never Repeats: the page's triangle counts == penrose.py's for every generation 0..9; total area unchanged at every
generation in the page too; the facts line reports half-triangle counts as diamonds; phone overflow 0; no errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "counts.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.penrose !== undefined")
    js = pg.evaluate("""() => [...Array(10).keys()].map(g => { const t = penroseApi.generate(g);
        const thin = t.filter(x => x[0] === 0).length; return {gen: g, thin, thick: t.length - thin, area: penroseApi.area(t)}; })""")
    check("counts == Python for generations 0..9", all((a["thin"], a["thick"]) == (b["thin"], b["thick"]) for a, b in zip(js, py)),
          str([(a["thin"], a["thick"]) for a in js][:6]))
    check("area unchanged at every generation (page)", all(abs(a["area"] - js[0]["area"]) < 1e-9 for a in js))
    for g in (0, 6, 8):
        pg.fill("#gen", str(g)); pg.dispatch_event("#gen", "input")
        st = pg.evaluate("window.penrose"); txt = pg.inner_text("#facts")
        check(f"slider at {g}: shown counts are the triangle counts", st["gen"] == g and f"{st['thick']} thick and {st['thin']} thin triangles" in txt
              and ("thick : thin" in txt) == (g >= 1), txt)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 900, "height": 1100}); pg.wait_for_timeout(300); pg.screenshot(path=str(D / "look.png"))
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
