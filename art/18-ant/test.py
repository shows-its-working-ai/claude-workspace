"""The Ant: the page's dark squares after 500, 5,000 and 11,000 steps == ant.py's exactly; the highway message is
absent at 9,976 and present at 9,977 (ant.py's start); Play advances; Skip lands on 9,000; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "ant.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.antApi !== undefined")
    pg.click("#play"); pg.wait_for_timeout(400); pg.click("#play")
    check("Play advances the ant", pg.evaluate("window.ant.t") > 0)
    pg.reload(); pg.wait_for_function("window.antApi !== undefined")
    for n in (500, 5000):
        pg.evaluate(f"antApi.run({n})")
        check(f"dark squares after {n} == Python", sorted(map(list, pg.evaluate("antApi.blackList()"))) == py["black"][str(n)])
    pg.click("#jump"); check("Skip lands on step 9,000", pg.evaluate("window.ant.t") == 9000)
    pg.evaluate(f"antApi.run({py['start'] - 1})"); before = pg.inner_text("#news")
    pg.evaluate(f"antApi.run({py['start']})"); after = pg.inner_text("#news")
    check(f"highway message: not at {py['start'] - 1}, yes at {py['start']}", "highway" not in before and "highway" in after and py["start"] == 9977)
    pg.evaluate("antApi.run(11000)")
    check("dark squares after 11000 == Python", sorted(map(list, pg.evaluate("antApi.blackList()"))) == py["black"]["11000"])
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.screenshot(path=str(D.parents[1] / "tools" / "_ant_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
