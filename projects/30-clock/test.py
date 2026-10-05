"""Clock Patience: the page's game logic == clock.py's on 3,000 random shuffles; the clickable game (deal a fixed deck,
then REAL clicks on 'Turn one card') ends exactly as the logic says, with every turned card face up; 'Play it out'
pressed twice runs ONE ticker (cards turned per 700 ms ~ 10, not ~ 20), and a new deal stops it; the tally counts
each finished game once; control: a deck the logic says WINS does come out on the page; phone 0; no JS errors."""
import json, random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {"__file__": str(D / "clock.py")}; exec((D / "clock.py").read_text(encoding="utf-8").split("small = {}")[0], ns)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
rng = random.Random(7); decks = []
for _ in range(3000):
    d = [k for k in range(13) for _ in range(4)]; rng.shuffle(d); decks.append(d)
win_deck = next(d for d in decks if ns["play"](list(d), 13, 4))
lose_deck = next(d for d in decks if not ns["play"](list(d), 13, 4))
def ids(ranks):                                   # rank list -> card ids (rank*4 + suit), suits handed out in order
    used = [0] * 13; out = []
    for r in ranks: out.append(r * 4 + used[r]); used[r] += 1
    return out
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.clock !== undefined")
    js = pg.evaluate("ds => ds.map(d => clockApi.play(d))", decks)
    py = [ns["play"](list(d), 13, 4) for d in decks]
    check("page logic == clock.py on 3,000 shuffles", js == py, f"{sum(py)} wins")
    for name, d, want in (("losing", lose_deck, False), ("winning (control)", win_deck, True)):
        pg.evaluate("d => clockApi.deal(d)", ids(d)); k = 0
        while not pg.evaluate("clock.over") and k < 60: pg.click("#turn"); k += 1
        s = pg.evaluate("window.clock"); msg = pg.inner_text("#msg")
        check(f"{name} deck by real clicks: ends as the logic says, every turned card face up",
              (s["turned"] == 52) == want and s["faceUp"] == s["turned"] == k and (("came out" in msg) == want), f"{k} clicks, {msg[:40]}")
    check("tally: two finished games, one came out", pg.evaluate("clock.played") == 2 and pg.evaluate("clock.won") == 1)
    pg.evaluate("d => clockApi.deal(d)", ids(lose_deck)); pg.click("#auto"); pg.click("#auto")
    pg.wait_for_timeout(700); n = pg.evaluate("clock.turned")
    check("'Play it out' pressed twice: one ticker (about 10 cards in 700 ms, not about 20)", 6 <= n <= 13, f"{n} turned")
    pg.click("#deal"); pg.wait_for_timeout(400)
    check("a new deal stops the old ticker", pg.evaluate("clock.turned") == 0)
    pg.click("#auto"); pg.wait_for_function("clock.over", timeout=15000)
    check("Play it out finishes a game; tally now 3", pg.evaluate("clock.played") == 3)
    OVL = """(() => { const b = [...document.querySelectorAll('.pile')].map(e => e.getBoundingClientRect()); let n = 0;
        for (let i = 0; i < b.length; i++) for (let j = 0; j < i; j++) if (b[i].left < b[j].right && b[j].left < b[i].right && b[i].top < b[j].bottom && b[j].top < b[i].bottom) n++; return n; })()"""
    check("no two piles overlap at desktop width", pg.evaluate(OVL) == 0)     # cycle 234: they did, at 2-3 and 8-9 o'clock
    pg.set_viewport_size({"width": 390, "height": 800})
    check("no two piles overlap at phone width", pg.evaluate(OVL) == 0, str(pg.evaluate(OVL)))
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 1100}); pg.evaluate("d => clockApi.deal(d)", ids(lose_deck))
    for _ in range(9): pg.click("#turn")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_clock_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
