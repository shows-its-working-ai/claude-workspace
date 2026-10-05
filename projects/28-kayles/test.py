"""Skittles (Kayles): the page's Grundy values == kayles.py's (first 200); following the Grundy strategy by REAL
clicks (both 'one' and 'two' modes) wins 10 and 13 pins; control: a bad opening (an end pin on 10) lets the computer
win; 'computer starts' pressed twice = one computer move; 'two' on a pin with no standing right-hand neighbour does
nothing; phone 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "kayles.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
BEST = """(() => { for (const m of skittlesApi.legal()){ const u = skittles.up.slice(); m.forEach(i => u[i] = false);
  let x = 0, run = 0; u.forEach(v => { if (v) run++; else { x ^= skittlesApi.G[run]; run = 0; } }); x ^= skittlesApi.G[run];
  if (x === 0) return m; } return skittlesApi.legal()[0]; })()"""
def move(pg, m):
    pg.click("#two" if len(m) == 2 else "#one"); pg.click(f"#lane button[data-i='{m[0]}']")
    pg.wait_for_function("skittles.over || skittles.turn === 'you'", timeout=5000)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.skittles !== undefined")
    check("page Grundy values == kayles.py (n < 200)", pg.evaluate("skittlesApi.G") == py["G"])
    for n in (10, 13):
        pg.click(f"[data-n='{n}']"); k = 0; modes = set()
        while not pg.evaluate("skittles.over") and k < 20:
            m = pg.evaluate(BEST); modes.add(len(m)); move(pg, m); k += 1
        check(f"{n} pins: the Grundy strategy, by real clicks, wins", "You win" in pg.inner_text("#msg"), f"{k} moves, modes used {sorted(modes)}")
    pg.click("[data-n='10']"); move(pg, [0]); k = 0
    while not pg.evaluate("skittles.over") and k < 20:
        move(pg, pg.evaluate("skittlesApi.legal()[0]")); k += 1
    check("control: opening with an end pin on 10 (leaves G(9) = 4, non-zero, for the computer) lets it win", "It wins" in pg.inner_text("#msg"))
    pg.click("[data-n='10']"); pg.click("#cpu"); pg.click("#cpu"); pg.wait_for_function("skittles.turn === 'you'"); pg.wait_for_timeout(900)
    check("'computer starts' twice: exactly one computer move (counted, not inferred from pins down)", pg.evaluate("skittles.cpuMoves") == 1 and pg.evaluate("skittles.turn") == "you", str(pg.evaluate("skittles.cpuMoves")))
    pg.click("[data-n='7']"); pg.click("#two"); pg.click("#lane button[data-i='6']")
    check("'two' on the last pin (no right-hand neighbour) knocks nothing", sum(pg.evaluate("skittles.up")) == 7 and "For two" in pg.inner_text("#msg"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.click("[data-n='13']"); pg.click("#one"); pg.click("#lane button[data-i='6']"); pg.wait_for_timeout(700)
    pg.screenshot(path=str(D.parents[1] / "tools" / "_kayles_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
