"""Corner the Queen: the page's safe squares == brute-force losing positions of Wythoff's game on the 12x12 board; the
computer's reply is legal everywhere and reaches a safe square whenever it can; the safe-square strategy played by
taps beats it from the start; a timid player (one step down each time) loses; bounded loops; phone; no errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
N = 12
lose = [[False] * N for _ in range(N)]
for a in range(N):
    for b in range(N):
        lose[a][b] = not (any(lose[a - k][b] for k in range(1, a + 1)) or any(lose[a][b - k] for k in range(1, b + 1))
                          or any(lose[a - k][b - k] for k in range(1, min(a, b) + 1)))
brute = {f"{a},{b}" for a in range(N) for b in range(N) if lose[a][b]}
def legal(a, b, x, y): return (x < a and y == b) or (x == a and y < b) or (a - x == b - y > 0)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.queenApi !== undefined")
    page_safe = {s for s in pg.evaluate("queenApi.SAFE()") if all(int(v) < N for v in s.split(","))}
    check(f"safe squares on the board == brute force ({len(brute)})", page_safe == brute, str(sorted(page_safe ^ brute)[:4]))
    bad = []
    for a in range(N):
        for b in range(N):
            if a == b == 0: continue
            x, y = pg.evaluate(f"queenApi.reply({a}, {b})")
            if not legal(a, b, x, y) or (not lose[a][b] and not lose[x][y]): bad.append((a, b, x, y))
    check("computer's reply: legal from all 143 squares, and reaches a safe square whenever it can", not bad, str(bad[:3]))
    pg.evaluate("queenApi.set(7, 9)")
    for _ in range(25):
        st = pg.evaluate("window.queen")
        if st["over"]: break
        a, b = st["q"]
        x, y = next((x, y) for x in range(N) for y in range(N) if legal(a, b, x, y) and lose[x][y])
        pg.click(f'#board button[data-x="{x}"][data-y="{y}"]')
    check("the safe-square strategy, by taps, beats the computer from (7, 9)", "You win" in pg.inner_text("#status"))
    pg.evaluate("queenApi.set(7, 9)")
    for _ in range(40):
        st = pg.evaluate("window.queen")
        if st["over"]: break
        a, b = st["q"]; x, y = (a, b - 1) if b else (a - 1, b)
        pg.click(f'#board button[data-x="{x}"][data-y="{y}"]')
    check("a timid player (one step at a time) loses", "It wins" in pg.inner_text("#status"))
    pg.evaluate("queenApi.set(5, 6)"); pg.check("#safe")
    check("'show the safe squares' marks them", pg.locator("#board .safe").count() == len(brute) - (1 if "5,6" in brute else 0))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    size = pg.evaluate("document.querySelector('#board button').getBoundingClientRect().width")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone: no overflow, squares >= 24 px, no JS errors", ov == 0 and size >= 24 and not errs, f"overflow={ov} size={size:.0f} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
