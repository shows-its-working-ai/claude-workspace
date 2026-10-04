"""Small Hex: the page's four computer openings == hex.py's winning first moves; the page's solver gives every one of
the 16 first moves the same verdict as hex.py; played by clicks: a winning opening + perfect play beats the computer,
a losing opening loses even with perfect play after, and when the computer starts it always wins (5 games); the
"can force a win" line agrees; every finished game has exactly one winner; phone 0; no JS errors."""
import json, sys, time
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
win1 = sorted(json.loads((D / "hex.json").read_text(encoding="utf-8"))["4"])
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.hexApi !== undefined")
    check("computer's openings == hex.py's winning first moves", sorted(pg.evaluate("hexApi.OPEN")) == win1 == [3, 6, 9, 12], str(win1))
    t = time.time()
    verdict = pg.evaluate("""() => [...Array(16)].map((_, i) => { const s = Array(16).fill(0); s[i] = 1;
        return hexApi.wins(s.join(''), 1) || hexApi.score(s.join(''), 2) < 0; })""")
    check("all 16 first moves: page verdict == hex.py", [i for i, v in enumerate(verdict) if v] == win1, f"{time.time() - t:.1f}s")
    def click_best():
        st = pg.evaluate("window.hex"); i = pg.evaluate(f"hexApi.bestMove('{st['board']}', {st['toMove']})")
        pg.click(f".cell[data-i='{i}']")
    def finish():
        for _ in range(16):
            if pg.evaluate("window.hex.over"): break
            click_best()
        return pg.evaluate("window.hex")
    pg.click("#new"); pg.click(".cell[data-i='6']")
    check("after a winning opening the line says Red (you) can force a win", "Red can force a win (that's you)" in pg.inner_text("#odds"))
    e = finish(); check("winning opening + perfect play beats the computer", e["red"] and not e["blue"], e["board"])
    pg.click("#new"); pg.click(".cell[data-i='0']")
    check("after a losing opening the line says Blue can force a win", "Blue can force a win" in pg.inner_text("#odds"))
    e = finish(); check("losing opening loses even with perfect play after", e["blue"] and not e["red"], e["board"])
    lost = []
    for _ in range(5):
        pg.click("#newc"); e = finish()
        if not (e["red"] and not e["blue"]): lost.append(e["board"])
    check("computer starts: it wins all 5 games against perfect play", not lost, str(lost))
    pg.click("#newc"); check("...'you're Blue'", "you're Blue" in pg.inner_text("#status"))
    # cycle 180: the first solver froze the page 4-7 s after your first move. Every cold first move must now be quick.
    worst = 0
    for cell in range(16):
        q = ctx.new_page(); q.goto((D / "index.html").as_uri()); q.wait_for_function("window.hexApi !== undefined")
        worst = max(worst, q.evaluate(f"() => {{ const t = performance.now(); document.querySelector(\".cell[data-i=\x27{cell}\x27]\").dispatchEvent(new MouseEvent(\x27click\x27, {{bubbles: true}})); return performance.now() - t; }}"))
        q.close()
    check("every cold first move blocks the page under 300 ms", worst < 300, f"worst {worst:.0f} ms")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D.parents[1] / "tools" / "_hex_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
