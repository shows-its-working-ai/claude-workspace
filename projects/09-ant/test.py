"""Langton's Ant page, checked against ant.py (an independent Python implementation).
Prediction (cycle 86, written first): onset between 9,000 and 11,000 -> Python found 9,977.
Checks: after "Run to step 12,500" the page reports the same onset as Python and the same number of black cells
(the 200x200 wrapping grid is big enough that the ant never wraps before step 12,500); Play advances; Reset clears;
phone overflow 0; no JS errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from ant import run, onset
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
turns, black, pos = run(12500); py_onset = onset(turns)
xs = [p[0] for p in black] + [pos[0]]; ys = [p[1] for p in black] + [pos[1]]
check("no wrap needed: python's pattern fits the page's 200x200 grid from its start (130,130)",
      130 + min(xs) >= 0 and 130 + max(xs) < 200 and 130 + min(ys) >= 0 and 130 + max(ys) < 200,
      f"x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    pg.click("#jump"); st = pg.evaluate("ant.state")
    check("page onset == Python onset", st["onset"] == py_onset == 9977, f"page {st['onset']}, python {py_onset}")
    check("ant ends where Python's does (catches a mirrored ant)", (st["dx"], st["dy"]) == pos, f"page {(st['dx'], st['dy'])}, python {pos}")
    check("black cells at step 12,500 == Python", st["steps"] == 12500 and st["black"] == len(black), f"page {st['black']}, python {len(black)}")
    check("highway message shown", "9,977" in pg.inner_text("#highway"))
    pg.click("#reset"); pg.click("#play"); pg.wait_for_timeout(600); s1 = pg.evaluate("ant.state")["steps"]; pg.click("#play")
    check("Play advances after Reset", s1 > 0 and pg.inner_text("#highway") == "", f"steps {s1}")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.click("#jump"); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
