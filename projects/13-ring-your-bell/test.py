"""Ring Your Bell: rows == Python's ringer; the scorer is right on hand-made taps; and a real run in the browser,
with a robot ringer pressing Space at its bell's times (by the audio clock), scores every strike on time, while a
robot that is 0.1 s late scores none on time but all near."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D.parents[1] / "writing"))
from ringing_15 import ring
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.ryb !== undefined")
    for name, pn, leads in (("Plain Hunt Minimus", ["x", "14"], 4), ("Plain Bob Minimus", ["x", "14", "x", "14", "x", "14", "x", "12"], 3)):
        check(f"{name}: rows == Python", pg.evaluate(f"ryb.rows({name!r})") == ["1234"] + ring(pn, leads))
    s = pg.evaluate("""() => { const e = [1, 2, 3, 4];
      return [ryb.score(e, [1, 2, 3, 4]), ryb.score(e, [1.1, 2.1, 3.1, 4.1]), ryb.score(e, [1.2, 2.2, 3.2, 4.2]),
              ryb.score(e, [1, 1.01, 2, 3, 4, 9])]; }""")
    check("scorer: perfect taps -> 4 on time", (s[0]["onTime"], s[0]["missed"]) == (4, 0))
    check("scorer: 100 ms late -> 0 on time, 4 near", (s[1]["onTime"], s[1]["close"]) == (0, 4))
    check("scorer: 200 ms late -> all missed, 4 extra", (s[2]["missed"], s[2]["extra"]) == (4, 4))
    check("scorer: double tap + stray -> 4 on time, 2 extra", (s[3]["onTime"], s[3]["extra"]) == (4, 2))
    sch = pg.evaluate("ryb.schedule('Plain Bob Minimus', 0.26)")
    check("schedule: two rounds, the extent, rounds: 27 rows, each bell once per row",
          len(sch["rows"]) == 27 and all(sorted(str(x["bell"]) for x in sch["strikes"] if x["row"] == i) == list("1234") for i in range(27)))
    # live runs: a robot presses Space by the audio clock (lag 0 and lag 0.1 s)
    for lag, want in ((0.0, "all"), (0.1, "none")):
        pg.select_option("#speed", "0.26"); pg.select_option("#bell", "3"); pg.click("#start")
        pg.evaluate("""(lag) => new Promise(done => {
            const step = () => {
              const r = window.__ryb_run && window.__ryb_run(); if (!r) return requestAnimationFrame(step);
              const el = r.ac.currentTime - r.t0;
              while (r.next < r.expected.length && el >= r.expected[r.next] + lag){
                document.dispatchEvent(new KeyboardEvent('keydown', {code: 'Space'})); r.next++; }
              if (r.next < r.expected.length) requestAnimationFrame(step); else done();
            }; step(); })""", lag)
        pg.wait_for_function("window.rybLast && document.getElementById('result').textContent.includes('of')", timeout=60000)
        r = pg.evaluate("window.rybLast"); pg.evaluate("window.rybLast = null")
        if want == "all": check(f"live run, robot on time: {r['onTime']}/{r['expected']} on time, mean error {r['meanErrMs']} ms",
                                r["onTime"] == r["expected"] == 27 and r["extra"] == 0)
        else: check(f"live run, robot 100 ms late: 0 on time, {r['close']} near", r["onTime"] == 0 and r["close"] == 27, str(r))
    # cycle 203: pressing Start again mid-run must not stack a second ringing (same bug as Blue Line, issue #1)
    pg.click("#start"); pg.wait_for_timeout(200); pg.click("#start"); pg.wait_for_timeout(200); pg.click("#start")
    check("pressing Start three times leaves exactly one ringing live", pg.evaluate("window.rybLive") == 1, str(pg.evaluate("window.rybLive")))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 900, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
