"""Checks Beat Rates in Claude's own browser: table vs Python, and table vs the
beat rate MEASURED from the rendered audio."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from beats import beat as pybeat

CASES = [(53, "M3"), (57, "M3"), (60, "M3"), (62, "m3"), (60, "M6"), (60, "P5"), (53, "P5"), (60, "P4")]
ok = True
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    for lo, iv in CASES:
        table = pg.evaluate(f"beatRate({lo}, '{iv}')")
        heard = pg.evaluate(f"measureBeat({lo}, '{iv}')")
        py = pybeat(lo, iv)
        err = abs(heard - table) / table
        good = abs(table - py) < 1e-9 and err < 0.08
        ok &= good
        print(f"lo={lo} {iv}: table {table:6.3f}  python {py:6.3f}  measured-from-audio {heard:6.3f}  ({err:5.1%}) {'ok' if good else 'FAIL'}")
    # practice: the audio really beats at the intended rate, and the answer key is right
    for diff in ("easy", "medium", "hard"):
        pg.select_option("#diff", diff)
        for _ in range(4):
            r = pg.evaluate("practice.newRound()")
            heard = pg.evaluate(f"measureFreqs({r['f1']}, {r['f2']}, {r['p']}, {r['q']})")
            key_ok = (r["played"] > r["target"]) == (r["answer"] == "faster")
            in_range = 53 <= r["lo"] and r["lo"] + (4 if r["iv"] == "M3" else 7) <= 65
            # The envelope-counting measurement is unreliable below ~1 beat/s (cycle 34: slow
            # fifths measured 1.5x-3x off). Measure the audio only where the method works; for
            # slow rounds check the exact algebra of the tones the page actually chose instead.
            if r["played"] >= 1.0:
                err = abs(heard - r["played"]) / r["played"]
            else:
                err = abs(abs(r["q"] * r["f2"] - r["p"] * r["f1"]) - r["played"]) / r["played"]
            good = key_ok and in_range and err < 0.08; ok &= good
            print(f"  {diff:6s} lo={r['lo']} {r['iv']}: target {r['target']:5.2f} played {r['played']:5.2f} "
                  f"measured {heard:5.2f} ({err:4.1%}) key={r['answer']:6s} {'ok' if good else 'FAIL'}")
    pg.evaluate("practice.newRound()")
    right = pg.evaluate("practice.answer(practice.round.answer)")
    print("  correct answer scored as right:", right); ok &= right is True
    # the crash fixed this cycle: practice tone playing, then table buttons pressed twice
    pg.click("#ptest"); pg.click("#t button >> nth=3"); pg.click("#t button >> nth=3"); pg.click("#pref")
    pg.wait_for_timeout(300)
    rows = pg.evaluate("document.querySelectorAll('#t tr').length - 1")
    pg.set_viewport_size({"width": 390, "height": 800})
    body_overflow = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    print("rows:", rows, "| page overflow at 390px:", body_overflow, "| js errors:", errs)
    ctx.close()
print("ALL PASS" if ok and rows == 13 and body_overflow == 0 and not errs else "FAILURES")
