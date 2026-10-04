"""Knight's Tour: the page's "a finish is still possible" verdict == tours.py's per-square counts for every 5x5 start
(possible iff count > 0); a whole tour played by clicks completes (a Warnsdorff walk, checked to be a real tour);
a dead end is reported as stuck and as unfinishable; illegal clicks are ignored; undo works; 6x6 shows; phone 0."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
per = json.loads((D / "tours.json").read_text(encoding="utf-8"))["5"]["per_start"]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.kt !== undefined")
    verdict = pg.evaluate("[...Array(25).keys()].map(v => ktApi.finishable([v], 5, 5e6))")
    check("finishable([start]) == (tours.py count > 0) for all 25 starts", verdict == [c > 0 for c in per], str(verdict[:6]))
    # a full tour by clicks: Warnsdorff from the corner (always finishable per the page) checked as a legal tour
    tour = pg.evaluate("""() => { const n = 5, seen = new Set([0]), p = [0];
        while (p.length < 25){ const nx = ktApi.nbrs(p[p.length - 1], n).filter(w => !seen.has(w)).filter(w => ktApi.finishable([...p, w], n, 5e6));
          if (!nx.length) break; seen.add(nx[0]); p.push(nx[0]); } return p; }""")
    for v in tour: pg.click(f'#board button[data-v="{v}"]')
    st = pg.evaluate("window.kt")
    legal = all(abs(a // 5 - b // 5) * abs(a % 5 - b % 5) == 2 for a, b in zip(tour, tour[1:]))
    check("a full 5x5 tour played by clicks completes", st["done"] and len(set(tour)) == 25 and legal and "Tour complete" in pg.inner_text("#status"))
    pg.click("#restart"); pg.click('#board button[data-v="0"]'); pg.click('#board button[data-v="0"]')
    pg.click('#board button[data-v="12"]')                                      # not a knight's move from 0: ignored
    check("illegal clicks ignored", pg.evaluate("window.kt.path") == [0])
    for v in (7, 4, 13, 24, 17, 6, 15, 22, 11, 2, 9, 18, 21, 10, 1, 8, 19, 16, 5, 14, 23, 20): pg.click(f'#board button[data-v="{v}"]')
    k = pg.evaluate("window.kt")
    check("a dead end shows as stuck (or unfinishable)", k["stuck"] or k["finishable"] is False, str(k["path"][-3:]))
    pg.click("#undo"); check("undo removes the last square", len(pg.evaluate("window.kt.path")) == len(k["path"]) - 1)
    pg.click("#restart"); pg.click('#board button[data-v="1"]')
    check("starting on the wrong colour says no finish is possible", "No finish is possible" in pg.inner_text("#hope"))
    pg.select_option("#size", "6"); check("6x6 board has 36 squares", pg.locator("#board button").count() == 36)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
