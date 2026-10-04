"""Pegs: the page's jump list == pegs.py's (36); its exact solvability agrees with Python on ALL 32,767 boards; from
every starting hole a one-peg finish is played by taps; a wrong move flips the hint to "no longer"; stuck is reported;
undo; tap targets 44+ px; phone overflow 0; no errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from pegs import JUMPS, solvable, FULL
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
sys.setrecursionlimit(10000)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.pegsApi !== undefined")
    js_j = sorted(tuple(j) for j in pg.evaluate("pegsApi.JUMPS"))
    check("jump list == Python (36 jumps)", js_j == sorted(JUMPS) and len(js_j) == 36, str(len(js_j)))
    js_s = pg.evaluate("(() => { const out = []; for (let b = 1; b < 32768; b++) out.push(pegsApi.solvable(b) ? 1 : 0); return out; })()")
    py_s = [1 if solvable(b) else 0 for b in range(1, FULL + 1)]
    check(f"solvability agrees on all 32,767 boards ({sum(js_s)} solvable)", js_s == py_s and sum(js_s) == 13935)
    wins = 0
    for start in range(15):
        pg.click("#restart"); pg.click(f'button[data-i="{start}"]')
        for _ in range(13):                         # cycle 145: bounded; 13 jumps take 14 pegs to 1
            if pg.evaluate("window.pegs.pegs") <= 1: break
            b = pg.evaluate("window.pegs.board")
            mv = next(m for m in JUMPS if b >> m[0] & 1 and b >> m[1] & 1 and not b >> m[2] & 1
                      and solvable(b & ~(1 << m[0]) & ~(1 << m[1]) | (1 << m[2])))
            pg.click(f'button[data-i="{mv[0]}"]'); pg.click(f'button[data-i="{mv[2]}"]')
            if pg.evaluate("window.pegs.board") == b: break      # the page refused a legal move: stop, it will count as a loss
        wins += "Solved" in pg.inner_text("#status")
    check("every one of the 15 starts is played to one peg by taps", wins == 15, f"{wins}/15")
    # a losing move: play winning moves from hole 0 until some legal move would lose, make THAT move, check the hint
    pg.click("#restart"); pg.click('button[data-i="0"]'); flipped = None; restored = False
    for _ in range(13):
        if pg.evaluate("window.pegs.pegs") <= 1 or flipped is not None: break
        b = pg.evaluate("window.pegs.board")
        legal = [m for m in JUMPS if b >> m[0] & 1 and b >> m[1] & 1 and not b >> m[2] & 1]
        after = lambda m: b & ~(1 << m[0]) & ~(1 << m[1]) | (1 << m[2])
        losing = [m for m in legal if not solvable(after(m))]
        if not legal: break
        m = losing[0] if losing else next((m for m in legal if solvable(after(m))), legal[0])
        pg.click(f'button[data-i="{m[0]}"]'); pg.click(f'button[data-i="{m[2]}"]')
        if losing:
            flipped = "no longer" in pg.inner_text("#hope") or pg.evaluate("window.pegs.stuck")
            pg.click("#undo"); restored = pg.evaluate("window.pegs.board") == b
    check("a losing move flips the hint to 'no longer' (or stuck)", flipped is True)
    check("undo after a move restores the board before it", restored)
    sizes = pg.evaluate("[...document.querySelectorAll('.hole')].map(e => Math.min(e.getBoundingClientRect().width, e.getBoundingClientRect().height))")
    check("every hole is at least 44 px", min(sizes) >= 44, str(min(sizes)))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
