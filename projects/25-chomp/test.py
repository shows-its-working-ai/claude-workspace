"""Poisoned Chocolate: the page's winning first moves == chomp.py's on every board up to 4x7; playing the solver's
moves by CLICKS beats the computer; a bad first move (top-right corner on 4x7) loses; 'computer starts' pressed twice
fast gives exactly ONE computer move (the cycle-204 bug class); poison can't be clicked mid-game; phone 0; no errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "chomp.json").read_text(encoding="utf-8"))["winning"]
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def wait_turn(pg): pg.wait_for_function("chomp.over || chomp.turn === 'you'", timeout=5000)
def click(pg, r, c): pg.click(f"#board button[data-r='{r}'][data-c='{c}']")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.chomp !== undefined")
    js = pg.evaluate("""() => { const o = {}; for (let r = 1; r <= 4; r++) for (let c = 1; c <= 7; c++) if (r * c > 1)
        o[`${r}x${c}`] = chompApi.winning(Array(r).fill(c)); return o; }""")
    check(f"winning first moves == chomp.py on {len(py)} boards", js == py)
    # perfect play by clicks, as the first player, on 4x7
    pg.click("[data-s='4x7']"); n = 0
    while not pg.evaluate("chomp.over") and n < 40:
        r, c = pg.evaluate("chompApi.winning(chomp.pos)[0]"); click(pg, r, c); wait_turn(pg); n += 1
    check("solver's moves by clicks beat the computer on 4x7", "You win" in pg.inner_text("#msg"), f"after {n} moves")
    # control: eat only the top-right square first, then play whatever the solver says (or anything)
    pg.click("[data-s='4x7']"); click(pg, 3, 6); wait_turn(pg); n = 0
    while not pg.evaluate("chomp.over") and n < 40:
        w = pg.evaluate("chompApi.winning(chomp.pos)")
        check("control: after a bad opening the human never has a winning move", not w) if n == 0 else None
        r, c = w[0] if w else pg.evaluate("(() => { const m = chompApi.moves(chomp.pos); return m[m.length - 1][0]; })()")
        click(pg, r, c); wait_turn(pg); n += 1
    check("bad first move (top-right) loses to the computer", "computer wins" in pg.inner_text("#msg"))
    # double-press 'computer starts'
    pg.click("[data-s='4x5']"); pg.click("#cstart"); pg.click("#cstart"); wait_turn(pg); pg.wait_for_timeout(900)
    eaten = 20 - sum(pg.evaluate("chomp.pos")); (wr, wc), = py["4x5"]; want = (4 - wr) * (5 - wc)
    check("'computer starts' twice: exactly one computer move, the winning one", pg.evaluate("chomp.turn") == "you" and eaten == want, f"eaten={eaten} want={want}")
    pg.click("#board button[data-r='0'][data-c='0']"); pg.wait_for_timeout(600)
    check("clicking the poison mid-game does nothing", 20 - sum(pg.evaluate("chomp.pos")) == want and not pg.evaluate("chomp.over"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900})
    pg.screenshot(path=str(D.parents[1] / "tools" / "_chomp_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
