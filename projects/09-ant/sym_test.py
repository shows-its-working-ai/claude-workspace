"""Multi-colour ant (cycle 88): the page's live symmetry indicator must agree with turmites.py at specific steps.
Python lists every even step <= 50,000 where LLRR (>= 100 cells) is exactly mirror-symmetric. The page must say
'symmetric' at three of those steps and NOT at three nearby even steps Python says aren't. Also: LLRR at 50,000
steps fits the page's 200x200 grid without wrapping; the plain ant (RL) behaviour is unchanged (onset 9,977)."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from turmites import sizes_at_symmetry
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
hits = {t for t, _ in sizes_at_symmetry("LLRR", 50_000)}
yes = [sorted(hits)[i] for i in (10, len(hits) // 2, -1)]
no = [t + 2 for t in yes if t + 2 not in hits][:3]
def extents(rule, steps):                       # every cell the ant ever touches, relative to its start
    x = y = 0; d = 0; n = len(rule); g = {}; xs = [0]; ys = [0]
    for _ in range(steps):
        c = g.get((x, y), 0); d = (d + (1 if rule[c] == "R" else -1)) % 4; g[(x, y)] = (c + 1) % n
        x += (0, 1, 0, -1)[d]; y += (-1, 0, 1, 0)[d]; xs.append(x); ys.append(y)
    return min(xs), max(xs), min(ys), max(ys)
x0, x1, y0, y1 = extents("LLRR", 50_000)
check("LLRR never wraps on the page's 200x200 grid from (130,130)", 130 + x0 >= 0 and 130 + x1 < 200 and 130 + y0 >= 0 and 130 + y1 < 200,
      f"x {x0}..{x1}, y {y0}..{y1}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    for t in sorted(yes + no):
        pg.evaluate("ant.setRule('LLRR')"); pg.evaluate(f"ant.advance({t})")
        got = pg.evaluate("ant.symmetric()") is not None
        check(f"LLRR step {t}: page says {'symmetric' if got else 'not symmetric'}, Python {'yes' if t in hits else 'no'}", got == (t in hits))
    pg.evaluate("ant.setRule('RL')"); pg.click("#jump")
    check("plain ant unchanged: onset 9,977", pg.evaluate("ant.state").get("onset") == 9977)
    pg.select_option("#rule", "LRRRRRLLR"); check("rule picker switches and resets", pg.evaluate("ant.state")["steps"] == 0)
    check("no JS errors", not errs, f"{errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
