"""Rose Lines: the page's petal counts (n = 1..12) and closing steps (d = 1..359) == maurer.py's; REAL keyboard input
on the sliders updates the drawing and caption (n 6 -> 7 flips 12 petals to 7; d 71 -> 72 drops 360 steps to 5);
control: the caption's numbers change only when the sliders do; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "maurer.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.rose !== undefined")
    check("petal counts n = 1..12 == maurer.py", pg.evaluate("[...Array(12)].map((_, i) => roseApi.tips(i + 1))") == [py["tips"][str(n)] for n in range(1, 13)])
    check("closing steps d = 1..359 == maurer.py", pg.evaluate("[...Array(359)].map((_, i) => roseApi.closes(i + 1))") == [py["closes"][str(d)] for d in range(1, 360)])
    s0 = pg.evaluate("window.rose"); c0 = pg.inner_text("#cap")
    pg.wait_for_timeout(300); check("control: nothing changes without input", pg.inner_text("#cap") == c0 and s0 == {"n": 6, "d": 71, "petals": 12, "steps": 360})
    pg.focus("#n"); pg.keyboard.press("ArrowRight"); s1 = pg.evaluate("window.rose")
    check("real ArrowRight on n: 6 -> 7, 12 petals -> 7", s1["n"] == 7 and s1["petals"] == 7 and "7 petals" in pg.inner_text("#cap"))
    pg.focus("#d"); pg.keyboard.press("ArrowRight"); s2 = pg.evaluate("window.rose")
    check("real ArrowRight on d: 71 -> 72, closes after 5 steps (shares 72 with 360)", s2["d"] == 72 and s2["steps"] == 5 and "after 5 steps" in pg.inner_text("#cap") and "share the factor 72" in pg.inner_text("#cap"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 1000}); pg.focus("#d"); pg.keyboard.press("ArrowLeft")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_maurer_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
