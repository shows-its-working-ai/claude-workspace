"""Find the Fox: the page's night-step == fox.py's on 2,000 random (set, look, n) cases; for 3-8 holes, fox.py's
shortest plan played by REAL clicks catches the fox on exactly the last day and says 'the best possible';
control: always looking in the middle (5 holes) is never a catch in 12 days; the hint shows exactly the possible
holes; Start again resets; phone 0; no JS errors."""
import json, random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {"__file__": str(D / "fox.py")}; exec((D / "fox.py").read_text(encoding="utf-8").split("res = {n:")[0], ns)
best = json.loads((D / "fox.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
rng = random.Random(243); cases = []
for _ in range(2000):
    n = rng.randint(1, 9); s = sorted(rng.sample(range(n), rng.randint(1, n))); cases.append((s, rng.randrange(n), n))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.fox !== undefined")
    js = pg.evaluate("cs => cs.map(([s, l, n]) => foxApi.step(s, l, n))", cases)
    py = [sorted(ns["step"](frozenset(s), l, n)) for s, l, n in cases]
    check("page night-step == fox.py on 2,000 cases", js == py)
    good = []
    for n in range(3, 9):
        plan = ns["solve"](n); pg.select_option("#n", str(n))
        for k, look in enumerate(plan):
            caught_early = pg.evaluate("fox.done"); pg.click(f"#holes button[data-i='{look}']")
        s = pg.evaluate("window.fox"); msg = pg.inner_text("#msg")
        good.append(s["done"] and s["day"] == len(plan) == best[str(n)] and "That is the best possible." in msg and not caught_early)   # not just "best possible": the other message says that too
    check("for 3-8 holes the shortest plan, by real clicks, catches it on exactly its last day", all(good), str(good))
    pg.select_option("#n", "5")
    for _ in range(12): pg.click("#holes button[data-i='2']")
    check("control: always the middle hole (5 holes) never catches it in 12 days", not pg.evaluate("fox.done") and pg.evaluate("fox.day") == 12)
    pg.click("#new"); pg.click("#show"); pg.click("#holes button[data-i='1']")
    shown = pg.evaluate("[...document.querySelectorAll('#holes button.maybe')].map(b => +b.dataset.i)")
    check("hint shows exactly the holes the fox could be in", shown == pg.evaluate("fox.maybe") == sorted(ns["step"](frozenset(range(5)), 1, 5)), str(shown))
    pg.click("#new"); check("Start again resets", pg.evaluate("fox.day") == 0 and pg.evaluate("fox.maybe") == [0, 1, 2, 3, 4])
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900})
    for i in (1, 2): pg.click(f"#holes button[data-i='{i}']")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_fox_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
