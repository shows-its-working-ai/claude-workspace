"""Code Breaker: the page's solver needs exactly knuth.json's number of guesses on all 1,296 codes; the page's scoring
== Python's on a sample of pairs; a game is won by clicking the colours; 10 wrong guesses lose and reveal the code;
Watch shows the same count; the other way round (cycle 166): 80 honestly scored games follow Knuth exactly, an
impossible answer is refused, a contradiction after 2+ consistent answers is reported as a slip; phone 0; no JS errors."""
import json, random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
sys.path.insert(0, str(D))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "knuth.json").read_text(encoding="utf-8"))
def score(g, s):
    b = sum(x == y for x, y in zip(g, s)); return [b, sum(min(g.count(c), s.count(c)) for c in "123456") - b]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.cbApi !== undefined")
    js = pg.evaluate("() => { const o = {}; for (const c of cbApi.CODES) o[c] = cbApi.knuth(c).length; return o; }")
    check("page solver == Python on all 1,296 codes", js == py, str([k for k in py if js.get(k) != py[k]][:4]))
    check("page solver never needs a sixth guess", max(js.values()) == 5)
    rnd = random.Random(165); pairs = [(rnd.choice(list(py)), rnd.choice(list(py))) for _ in range(3000)] + [("1122", "2211"), ("1111", "1112"), ("1234", "4321")]
    jsS = pg.evaluate("ps => ps.map(([g, s]) => cbApi.score(g, s))", pairs)
    check("page scoring == Python on 3,003 pairs", jsS == [score(g, s) for g, s in pairs])
    def play(code):
        for c in code: pg.click(f"#pal button[data-c='{c}']")
        pg.click("#go")
    pg.evaluate("cbApi.newGame('6153')")
    for st in pg.evaluate("cbApi.knuth('6153').map(s => s.guess)"): play(st)
    st = pg.evaluate("window.cb")
    check("won by clicks following the solver", st["over"] and st["rows"][-1]["fb"] == [4, 0] and len(st["rows"]) == py["6153"], f"{len(st['rows'])} rows")
    check("win message", "Broken in" in pg.inner_text("#msg"))
    pg.click("#watch"); check("Watch shows the same count", f"needed {py['6153']}." in pg.inner_text("#log"))
    pg.evaluate("cbApi.newGame('2222')")
    for _ in range(10): play("1111")
    st = pg.evaluate("window.cb")
    check("10 wrong guesses lose and reveal the code", st["over"] and "Out of guesses" in pg.inner_text("#msg") and pg.locator("#msg .peg").count() == 4)
    check("palette disabled after the game", pg.locator("#pal button[disabled]").count() == 6)
    # cycle 166: the other way round. An honest player scores the page's guesses for a sample of codes.
    codes = sorted(py, key=lambda c: -py[c])[:20] + random.Random(166).sample(sorted(py), 60)
    wrong = []
    for code in codes:
        pg.click('#rnew'); seen = []
        for _ in range(8):
            r = pg.evaluate('window.cbRev')
            if r['done']: break
            seen.append(r['guess']); b, w = score(r['guess'], code)
            pg.select_option('#rb', str(b)); pg.select_option('#rw', str(w)); pg.click('#rgo')
        r = pg.evaluate('window.cbRev')
        if not (r['done'] and seen == pg.evaluate(f"cbApi.knuth('{code}').map(s => s.guess)") and 'Got it in' in r['msg']): wrong.append((code, seen))
    check(f'other way round: {len(codes)} honest games follow Knuth exactly and finish', not wrong, str(wrong[:2]))
    check('...including all 20 that need five', all(py[c] == 5 for c in codes[:20]))
    pg.click('#rnew'); pg.select_option('#rb', '3'); pg.select_option('#rw', '1'); pg.click('#rgo')
    r = pg.evaluate('window.cbRev'); check('3 right + 1 wrong place is refused', r['rows'] == 0 and "can't happen" in r['msg'])
    # answer consistently until some legal answer would fit no code at all, then give that one
    pg.click('#rnew'); left = list(py); fbs = [(b, w) for b in range(4) for w in range(5) if b + w <= 4 and (b, w) != (3, 1)]
    slip = None
    for step in range(6):
        g = pg.evaluate('window.cbRev.guess')
        bad = [f for f in fbs if step >= 2 and not any(score(g, s) == list(f) for s in left)
               and any(score(g, s) == list(f) for s in py)]          # fits some code, just not the earlier answers
        f = bad[0] if bad else max(fbs, key=lambda f: sum(score(g, s) == list(f) for s in left))
        pg.select_option('#rb', str(f[0])); pg.select_option('#rw', str(f[1])); pg.click('#rgo')
        if bad: slip = (g, f); break
        left = [s for s in left if score(g, s) == list(f)]
    r = pg.evaluate('window.cbRev')
    check(f'contradictory answer {slip} after 2+ consistent answers is caught as a slip', slip and r['rows'] >= 3 and r['done'] and 'slip' in r['msg'] and not pg.is_visible('#rform'), str(r))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D.parents[1] / "tools" / "_cb_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
