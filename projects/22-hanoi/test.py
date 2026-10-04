"""Towers and Map: the page's moves give the same distances as hanoi.py from the start, for 3..6 disks; the map
has 3^n dots in 3^n distinct places; the recursive solution, clicked in, finishes in 2^n - 1 with the "fewest
possible" message (n = 3, 4, 5); an illegal move (bigger on smaller) is refused; phone 0; no JS errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {}; exec((D / "hanoi.py").read_text(encoding="utf-8").split("bad = []")[0], ns)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def solve(k, a, c, b, out):
    if k: solve(k - 1, a, b, c, out); out.append((a, c)); solve(k - 1, b, c, a, out)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.hanoiApi !== undefined")
    for n in (3, 4, 5, 6):
        pg.click(f"#sizes button[data-n='{n}']")
        js = pg.evaluate("""() => { const st = Array(window.hanoi.n).fill(0), d = new Map([[st.join(''), 0]]), q = [st];
            for (let i = 0; i < q.length; i++) for (const t of hanoiApi.legal(q[i])){ const k = t.join(''); if (!d.has(k)){ d.set(k, d.get(q[i].join('')) + 1); q.push(t); } }
            return Object.fromEntries(d); }""")
        py, _ = ns["bfs"]((0,) * n)
        check(f"n={n}: page's moves reach the same {len(py)} positions at the same distances", js == {"".join(map(str, s)): v for s, v in py.items()})
        places = pg.evaluate("hanoiApi.all().map(s => hanoiApi.where(s).map(v => v.toFixed(3)).join(','))")
        check(f"n={n}: map has {3 ** n} dots in {len(set(places))} distinct places", pg.evaluate("window.hanoi.dots") == 3 ** n == len(set(places)))
        # cycle 186: the first layout drew long lines across the map; in the right one every move is the same short step
        L = pg.evaluate("""() => { const out = []; for (const s of hanoiApi.all()) for (const t of hanoiApi.legal(s)){
            const [a, b] = hanoiApi.where(s), [c, d] = hanoiApi.where(t); out.push(Math.hypot(a - c, b - d)); } return [Math.min(...out), Math.max(...out)]; }""")
        check(f"n={n}: every line on the map is the same length", L[1] / L[0] < 1.0001, f"{L[0]:.2f}..{L[1]:.2f}")
    for n in (3, 4, 5):
        pg.click(f"#sizes button[data-n='{n}']"); seq = []; solve(n, 0, 2, 1, seq)
        for a, c in seq: pg.click(f".peg[data-p='{a}']"); pg.click(f".peg[data-p='{c}']")
        h = pg.evaluate("window.hanoi")
        check(f"n={n}: recursive solution clicked in: done in {2 ** n - 1}, 'fewest possible'", h["done"] and h["moves"] == 2 ** n - 1 and "the fewest possible" in pg.inner_text("#status"))
    pg.click("#sizes button[data-n='3']"); pg.click(".peg[data-p='0']"); pg.click(".peg[data-p='1']")    # smallest to peg 2
    pg.click(".peg[data-p='0']"); pg.click(".peg[data-p='1']")                                            # middle onto smallest: illegal
    h = pg.evaluate("window.hanoi")
    check("illegal move (bigger on smaller) refused", h["moves"] == 1 and h["state"] == [1, 0, 0])
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.click("#sizes button[data-n='4']")
    for a, c in [(0, 1), (0, 2), (1, 2), (0, 1)]: pg.click(f".peg[data-p='{a}']"); pg.click(f".peg[data-p='{c}']")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_hanoi_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
