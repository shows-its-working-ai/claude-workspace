"""Eight: the page's distance for all 181,440 positions == eight.py's; following the Hint from a hardest position
solves it in exactly 31 taps; arrow keys move the right tile; Swap two tiles -> "never"; Shuffle lands on a solvable
position; buttons wait for the distances; phone overflow 0; no JS errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {}; exec((D / "eight.py").read_text(encoding="utf-8").split("def inversions")[0], ns); py = ns["dist"]
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    early = pg.evaluate("eightApi.isReady() ? \"already ready\" : [\"hint\", \"shuffle\", \"hardest\", \"swap\"].every(b => document.getElementById(b).disabled)")
    check("before distances are ready, all four buttons are disabled", early is True, f"saw: {early}")
    pg.wait_for_function("eightApi.isReady()", timeout=20000)
    js = pg.evaluate("eightApi.dist()")
    check("page distances == Python on all 181,440", js == py, f"{len(js)} vs {len(py)}")
    pg.click("#hardest"); s0 = pg.evaluate("window.eight.state")
    taps = 0
    while pg.evaluate("window.eight.dist") and taps < 40:
        pg.click("#hint"); pg.click("#grid button.hint"); taps += 1
    e = pg.evaluate("window.eight")
    check(f"hint path from {s0} solves in exactly 31", s0 in ("647850321", "867254301") and e["state"] == "123456780" and taps == 31 and e["moves"] == 31, f"{taps} taps")
    check("says solved in 31", "Solved in 31 moves" in pg.inner_text("#status"))
    pg.evaluate("eightApi.set('123456708')"); pg.keyboard.press("ArrowLeft")
    check("ArrowLeft slides 8 into the gap -> solved", pg.evaluate("window.eight.state") == "123456780")
    pg.keyboard.press("ArrowLeft"); check("ArrowLeft with nothing to its right does nothing", pg.evaluate("window.eight.state") == "123456780")
    pg.click("#swap"); e = pg.evaluate("window.eight")
    check("swap two tiles -> unreachable, page says never", e["state"] not in py and e["dist"] is None and "never" in pg.inner_text("#status"))
    bad = []
    for _ in range(20):
        pg.click("#shuffle"); s = pg.evaluate("window.eight.state")
        if s not in py or s == "123456780": bad.append(s)
    check("20 shuffles all solvable and not already solved", not bad, str(bad))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
