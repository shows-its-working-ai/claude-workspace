"""Nobody Wins Noughts: the page's verdict on all 230 reachable safe positions == notakto.py's; played by clicks:
centre + perfect play beats the computer, a corner opening loses to it, the computer starting wins 5/5 against
perfect play; with no safe squares the status says so and any move loses; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "notakto.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.notaktoApi !== undefined")
    js = pg.evaluate("ms => Object.fromEntries(ms.map(m => [m, notaktoApi.wins(+m)]))", list(py))
    check(f"page verdicts == Python on all {len(py)} safe positions", js == py and len(py) == 230)
    def my_best():                                                   # perfect play for the human, using the page's own solver
        m = pg.evaluate("window.notakto.mask"); return pg.evaluate(f"notaktoApi.choose({m})")
    seen = []                                                        # status shown before each of the human's moves
    def finish():
        seen.clear()
        for _ in range(12):
            st = pg.evaluate("window.notakto")
            if st["over"]: return st
            if st["turnIsYours"]: seen.append(pg.inner_text("#status")); pg.click(f"#grid button[data-i='{my_best()}']")
            else: pg.wait_for_timeout(300)
        return pg.evaluate("window.notakto")
    pg.click("#new"); pg.click("#grid button[data-i='4']"); st = finish()
    check("centre + perfect play beats the computer", st["over"] and not st["youLost"])
    pg.click("#new"); pg.click("#grid button[data-i='0']"); st = finish()
    check("a corner opening loses, even with perfect play after", st["over"] and st["youLost"])
    check("...and before the forced losing move the status said there were no safe squares", seen and "No safe squares left" in seen[-1], seen[-1:] )
    lost = 0
    for _ in range(5):
        pg.click("#newc"); pg.wait_for_timeout(350); lost += finish()["youLost"]
    check("computer starts: it wins 5 of 5 against perfect play", lost == 5)
    st = pg.evaluate("window.notakto")
    check("a lost game says so, with the line marked", "you lose" in pg.inner_text("#status") and pg.locator("#grid button.bad").count() == 3)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
