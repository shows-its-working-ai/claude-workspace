"""Nim: the page's reply is legal everywhere and makes the XOR 0 whenever that's possible (all 3-heap positions up to 7,
4-heap up to 5); a player using the XOR strategy by taps beats the computer from 3-5-7; a player who always takes 1
from the first non-empty row loses to it from 3-5-7; win/lose messages and game-over; hint text; tap sizes; phone."""
import sys
from itertools import product
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def xor(h):
    x = 0
    for v in h: x ^= v
    return x
positions = [list(h) for h in product(range(8), repeat=3)] + [list(h) for h in product(range(6), repeat=4)]
positions = [h for h in positions if any(h)]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.nimApi !== undefined")
    replies = pg.evaluate("ps => ps.map(h => nimApi.reply(h))", positions)
    illegal = [(h, r) for h, r in zip(positions, replies) if not (0 <= r[0] < len(h) and 1 <= r[1] <= h[r[0]])]
    missed = [(h, r) for h, r in zip(positions, replies) if xor(h) and xor([v - (r[1] if i == r[0] else 0) for i, v in enumerate(h)])]
    check(f"computer's reply is legal in all {len(positions)} positions", not illegal, str(illegal[:2]))
    check("...and always leaves XOR 0 when it can", not missed, str(missed[:2]))
    def tap_take(i, n):                          # take n from row i by tapping the right stone
        h = pg.evaluate("window.nim.heaps"); pg.click(f'button.stone[data-row="{i}"][data-k="{h[i] - n}"]')
    # the XOR player from 3-5-7
    pg.evaluate("nimApi.set([3, 5, 7])")
    for _ in range(20):
        st = pg.evaluate("window.nim")
        if st["over"]: break
        h = st["heaps"]; x = xor(h)
        i = next(i for i, v in enumerate(h) if v ^ x < v); tap_take(i, h[i] - (h[i] ^ x))
    check("the XOR strategy, played by taps, beats the computer from 3-5-7", "You win" in pg.inner_text("#status"))
    pg.evaluate("nimApi.set([3, 5, 7])")
    for _ in range(30):
        st = pg.evaluate("window.nim")
        if st["over"]: break
        i = next(i for i, v in enumerate(st["heaps"]) if v); tap_take(i, 1)
    check("a naive player (always take 1) loses to the computer", "It wins" in pg.inner_text("#status"))
    pg.evaluate("nimApi.set([1, 2, 3])"); pg.check("#showhint")
    check("hint says losing at XOR 0 (1-2-3)", "losing" in pg.inner_text("#hint"))
    pg.evaluate("nimApi.set([3, 5, 7])")
    check("hint says winnable at 3-5-7", "can win" in pg.inner_text("#hint"))
    sizes = pg.evaluate("[...document.querySelectorAll('.stone')].map(e => e.getBoundingClientRect().width)")
    check("stones are at least 36 px", min(sizes) >= 36, str(min(sizes)))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
