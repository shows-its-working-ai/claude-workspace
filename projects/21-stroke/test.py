"""One Stroke: for every figure on the page, the page's verdict (Euler's rule) == brute force over every drawing;
each possible figure is drawn completely by clicks along a brute-force path; each impossible one gets stuck and the
hint says impossible; starting a two-odd-point figure at an even point always gets stuck; undo works; phone 0."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def all_paths(n, edges, start=None):                         # every complete one-stroke drawing, as point sequences
    out, used = [], [False] * len(edges)
    def go(p):
        if all(used): out.append(list(p)); return
        for k, (a, b) in enumerate(edges):
            if not used[k] and p[-1] in (a, b):
                used[k] = True; p.append(b if p[-1] == a else a); go(p); p.pop(); used[k] = False
    for s in ([start] if start is not None else range(n)): go([s])
    return out
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.strokeApi !== undefined")
    figs = pg.evaluate("strokeApi.FIGS")
    check("six figures, at least two impossible", len(figs) == 6 and sum(not pg.evaluate(f"strokeApi.verdict(strokeApi.FIGS[{i}]).possible") for i in range(6)) >= 2)
    for i, f in enumerate(figs):
        n, edges = len(f["pts"]), [tuple(e) for e in f["edges"]]
        paths = all_paths(n, edges); page_possible = pg.evaluate(f"strokeApi.verdict(strokeApi.FIGS[{i}]).possible")
        check(f"{f['name']}: page says {'possible' if page_possible else 'impossible'}, brute force found {len(paths)} drawings", page_possible == bool(paths))
        pg.click(f"#figs button[data-f='{i}']")
        if paths:
            for v in paths[0]: pg.click(f".pt[data-i='{v}']", force=True)
            check(f"  drawn completely by clicks", pg.evaluate("window.stroke.done") and "Done" in pg.inner_text("#status"))
            odd = pg.evaluate("window.stroke.odd")
            if len(odd) == 2:
                ev = next(v for v in range(n) if v not in odd)
                check(f"  starting at even point {ev}: no drawing exists (brute force)", not all_paths(n, edges, ev))
        else:
            pg.click(f".pt[data-i='0']", force=True)
            for _ in range(20):
                st = pg.evaluate("window.stroke")
                if st["stuck"]: break
                here = st["path"][-1]; usedk = len(st["path"]) - 1
                nxt = [b if a == here else a for a, b in edges if here in (a, b)]
                for w in nxt:
                    before = len(pg.evaluate("window.stroke.path")); pg.click(f".pt[data-i='{w}']", force=True)
                    if len(pg.evaluate("window.stroke.path")) > before: break
            check(f"  gets stuck when tried", pg.evaluate("window.stroke.stuck") and "Stuck" in pg.inner_text("#status"))
            pg.click("#restart"); pg.click(f".pt[data-i='0']", force=True); pg.click("#hint")
            check(f"  hint says impossible", "Impossible" in pg.inner_text("#status"))
    pg.click("#figs button[data-f='4']"); pg.click(".pt[data-i='0']", force=True); pg.click(".pt[data-i='1']", force=True)
    pg.click("#undo"); check("undo takes back the last line", pg.evaluate("window.stroke.path") == [0] and pg.evaluate("window.stroke.left") == 5)
    pg.click("#figs button[data-f=\x271\x27]"); pg.click("#hint")
    check("hint works before any point is tapped", "Impossible" in pg.inner_text("#status"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.click("#figs button[data-f='0']"); pg.click("#hint")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_stroke_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
