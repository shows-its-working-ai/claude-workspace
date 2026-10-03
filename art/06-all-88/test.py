"""All 88 (cycle 81). Prediction (written first, about the automata, not my code): Rule 110 lands between 10th and
30th most incompressible of the 88 (cycle 1 found it 14th with a different measure).
Independent check: Python rebuilds the same 88 patterns (same LCG start, numpy), compresses with zlib (raw deflate,
level 6), and the page's ORDER must agree closely (Spearman rank correlation > 0.98). Also: exactly 88 panels,
every link opens Rule Explorer at that rule, phone overflow 0, no JS errors."""
import sys, zlib
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
W = T = 120
def mirror(r): return sum(((r >> (4 * a + 2 * b + c)) & 1) << (4 * c + 2 * b + a) for a in (0, 1) for b in (0, 1) for c in (0, 1))
def comp(r): return sum((1 - ((r >> (7 - n)) & 1)) << n for n in range(8))
reps = sorted({min(r, mirror(r), comp(r), comp(mirror(r))) for r in range(256)})
def start():
    s, out = 2026, []
    for _ in range(W): s = (s * 1664525 + 1013904223) % 2 ** 32; out.append(1 if s / 2 ** 32 < 0.5 else 0)
    return np.array(out, dtype=np.uint8)
def size(r):
    tab = np.array([(r >> i) & 1 for i in range(8)], dtype=np.uint8); row = start(); h = [row]
    while len(h) < T: row = tab[4 * np.roll(row, 1) + 2 * row + np.roll(row, -1)]; h.append(row)
    c = zlib.compressobj(6, zlib.DEFLATED, -15); return len(c.compress(np.packbits(np.array(h).ravel()).tobytes()) + c.flush())
py = sorted(reps, key=lambda r: (-size(r), r))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.all88 !== undefined", timeout=20000)
    js = pg.evaluate("window.all88"); order = [x["r"] for x in js]
    check("88 panels, same 88 rules as Python", len(order) == 88 and sorted(order) == reps)
    rank_js = {r: i for i, r in enumerate(order)}; rank_py = {r: i for i, r in enumerate(py)}
    d2 = sum((rank_js[r] - rank_py[r]) ** 2 for r in reps); rho = 1 - 6 * d2 / (88 * (88 ** 2 - 1))
    check("page order agrees with independent zlib order (Spearman > 0.98)", rho > 0.98, f"rho = {rho:.4f}")
    r110 = rank_js[110] + 1
    print(f"     Rule 110 rank: page {r110}, Python {rank_py[110] + 1} (prediction: 10-30)")
    hrefs = pg.eval_on_selector_all("#grid a", "as => as.map(a => a.getAttribute('href'))")
    check("every panel links to Rule Explorer at its rule", hrefs == [f"../../projects/08-rules/index.html#{r}" for r in order])
    pg.goto((D.parents[1] / "projects" / "08-rules" / "index.html").as_uri() + "#54")
    check("Rule Explorer opens #54 at rule 54", pg.evaluate("rx.rule") == 54)
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.all88 !== undefined")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 1000, "height": 900}); pg.screenshot(path=str(D / "look.png"))
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
