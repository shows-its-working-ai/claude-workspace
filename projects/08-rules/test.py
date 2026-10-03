"""Rule Explorer checks, in Claude's own browser.
Prediction (written first): for ALL 256 rules, the page's simulation (60 steps from one cell) equals an independent
numpy simulation; its mirror/complement twins equal Python's; and the twin classes number exactly 88 (the known
count of inequivalent elementary rules). UI: clicking a table entry flips exactly that bit; typing a number sets
the rule; clicking a twin loads it; phone overflow 0; no JS errors."""
import sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
W, N = 301, 60
def py_hist(r):
    table = np.array([(r >> i) & 1 for i in range(8)], dtype=np.uint8)
    row = np.zeros(W, dtype=np.uint8); row[W // 2] = 1; h = [row]
    for _ in range(N - 1): row = table[4 * np.roll(row, 1) + 2 * row + np.roll(row, -1)]; h.append(row)
    return np.array(h)
def py_mirror(r): return sum(((r >> (4 * a + 2 * b + c)) & 1) << (4 * c + 2 * b + a) for a in (0, 1) for b in (0, 1) for c in (0, 1))
def py_comp(r): return sum((1 - ((r >> (7 - n)) & 1)) << n for n in range(8))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    js_all = pg.evaluate(f"[...Array(256).keys()].map(r => rx.history(r, 'single', {N}))")
    bad = [r for r in range(256) if not np.array_equal(np.array(js_all[r], dtype=np.uint8), py_hist(r))]
    check("all 256 rules: page simulation == numpy", not bad, f"mismatches {bad[:5]}")
    tw = pg.evaluate("[...Array(256).keys()].map(r => [rx.mirror(r), rx.complement(r)])")
    badt = [r for r in range(256) if tw[r] != [py_mirror(r), py_comp(r)]]
    check("all 256 rules: mirror and complement == Python", not badt, f"{badt[:5]}")
    classes = {tuple(sorted({r, py_mirror(r), py_comp(r), py_comp(py_mirror(r))})) for r in range(256)}
    jsc = pg.evaluate("new Set([...Array(256).keys()].map(r => rx.twins(r).join(','))).size")
    check("88 equivalence classes (Python and page)", len(classes) == 88 and jsc == 88, f"py {len(classes)}, page {jsc}")
    check("known facts: 110's twins are 124, 137, 193", pg.evaluate("rx.twins(110)") == [110, 124, 137, 193])
    # UI
    pg.click('.rule[data-n="0"]'); check("click flips bit 0: 110 -> 111", pg.evaluate("rx.rule") == 111)
    pg.click('.rule[data-n="0"]'); pg.click('.rule[data-n="7"]'); check("click bit 7: 110 -> 238", pg.evaluate("rx.rule") == 238)
    pg.fill("#num", "30"); check("typing 30 sets rule 30", pg.evaluate("rx.rule") == 30)
    pg.locator("#twins a").first.click(); check("clicking a twin loads it", pg.evaluate("rx.rule") in (86, 135, 149))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
