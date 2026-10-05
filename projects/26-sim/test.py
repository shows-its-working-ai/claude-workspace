"""No Triangles (Sim): page verdicts == sim.py on 700 positions; as SECOND player, the solver's moves made by REAL
clicks beat the computer; as first player (any safe moves) you lose; 'computer starts' twice = one computer move;
every one of the 15 lines can be picked by a real click at a point where it's clearly nearest; a real TOUCHSCREEN tap
at phone width picks the right line; control: a click far from every line picks nothing; phone 0; no JS errors."""
import json, math, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser, open_touch
from playwright.sync_api import sync_playwright
py = json.loads((D / "sim.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def seg_d(x, y, a, b):
    (x1, y1), (x2, y2) = a, b; dx, dy = x2 - x1, y2 - y1
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy))); return math.hypot(x - x1 - t * dx, y - y1 - t * dy)
def spot(P, E, i):                     # a point on line i at least 12 units from every other line
    a, b = P[E[i][0]], P[E[i][1]]
    for k in range(20, 81):
        t = k / 100; x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
        if all(seg_d(x, y, P[E[j][0]], P[E[j][1]]) > 12 for j in range(15) if j != i): return x, y
def click_line(pg, i, touch=False):
    P, E = pg.evaluate("simApi.P"), pg.evaluate("simApi.E"); x, y = spot(P, E, i)
    pg.evaluate("document.getElementById('board').scrollIntoView({block: 'center'})"); b = pg.locator("#board").bounding_box()
    sx, sy = b["x"] + x / 400 * b["width"], b["y"] + y / 400 * b["height"]
    (pg.touchscreen.tap if touch else pg.mouse.click)(sx, sy)
def wait(pg): pg.wait_for_function("sim.over || sim.turn === 'you'", timeout=5000)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.sim !== undefined")
    js = pg.evaluate("ps => ps.map(([m, t]) => simApi.wins(m, t))", py["positions"])
    check(f"page verdicts == sim.py on {len(js)} positions", js == [w for _, _, w in py["positions"]])
    check("page: first player loses from the empty board", pg.evaluate("simApi.wins(0, 0)") is False and py["first_player_wins"] is False)
    P, E = pg.evaluate("simApi.P"), pg.evaluate("simApi.E")
    check("every line has a clear spot to click", all(spot(P, E, i) for i in range(15)))
    picked = []
    for i in range(15):
        pg.click("#youfirst"); click_line(pg, i); picked.append(pg.evaluate("sim.you") == 1 << i)
    check("a real click picks each of the 15 lines, and only it", all(picked), str([i for i, g in enumerate(picked) if not g]))
    # as second player, follow the solver
    pg.click("#cpufirst"); wait(pg); n = 0
    while not pg.evaluate("sim.over") and n < 10:
        mv = pg.evaluate("""(() => { const y = sim.you, c = sim.cpu; for (let i = 0; i < 15; i++){ const b = 1 << i;
            if ((y | c) & b || simApi.tri(y | b)) continue; if (!simApi.wins(c, y | b)) return i; } return -1; })()""")
        click_line(pg, mv); wait(pg); n += 1
    check("second player, solver's moves by real clicks: you win", "You win" in pg.inner_text("#msg"), pg.inner_text("#msg"))
    # as first player, any safe move: you lose
    pg.click("#youfirst"); n = 0
    while not pg.evaluate("sim.over") and n < 10:
        mv = pg.evaluate("""(() => { const y = sim.you, c = sim.cpu; let any = -1; for (let i = 0; i < 15; i++){ const b = 1 << i;
            if ((y | c) & b) continue; if (any < 0) any = i; if (!simApi.tri(y | b)) return i; } return any; })()""")
        click_line(pg, mv); wait(pg); n += 1
    check("first player against perfect play: you lose", "You lose" in pg.inner_text("#msg"), pg.inner_text("#msg"))
    pg.click("#cpufirst"); pg.click("#cpufirst"); wait(pg); pg.wait_for_timeout(900)
    check("'computer starts' twice: exactly one computer line", bin(pg.evaluate("sim.cpu")).count("1") == 1 and pg.evaluate("sim.you") == 0)
    pg.click("#youfirst"); b = pg.locator("#board").bounding_box(); pg.mouse.click(b["x"] + 4, b["y"] + 4)
    check("control: a click in the corner, far from every line, picks nothing", pg.evaluate("sim.you") == 0)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.click("#cpufirst"); wait(pg)
    pg.screenshot(path=str(D.parents[1] / "tools" / "_sim_look.png"), full_page=True)
    ctx.close()
    tc = open_touch(p); tp = tc.new_page(); tp.goto((D / "index.html").as_uri()); tp.wait_for_function("window.sim !== undefined")
    got = []
    for i in (0, 7, 14):
        tp.click("#youfirst"); click_line(tp, i, touch=True); got.append(tp.evaluate("sim.you") == 1 << i)
    check("real touchscreen taps at phone width pick lines 0, 7, 14", all(got), str(got))
    tc.close()
print("ALL PASS" if ok else "FAILURES")
