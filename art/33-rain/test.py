"""Rain on a Window: only the mechanics, since the look can't be checked. It draws (the picture isn't flat); it moves
while playing, and a REAL click on Pause freezes it pixel for pixel, Play moves it again; the rain slider by keyboard
changes how many drops there are (heavier = more); 'Another street' changes the lights behind; reduced motion starts
paused; phone width; no JS errors. Control: two snapshots taken back to back while PLAYING differ, so 'paused = same
pixels' is a real distinction, not a page that never changes."""
import hashlib, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
SNAP = "() => document.getElementById('cv').toDataURL()"
h = lambda s: hashlib.md5(s.encode()).hexdigest()[:8]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.rain && window.rain.playing")
    spread = pg.evaluate("""() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        let lo = 255, hi = 0; for (let i = 0; i < d.length; i += 4){ const v = (d[i] + d[i + 1] + d[i + 2]) / 3; lo = Math.min(lo, v); hi = Math.max(hi, v); } return hi - lo; }""")
    check("it draws: the picture isn't flat (brightness spread > 100)", spread > 100, f"{spread:.0f}")
    a = h(pg.evaluate(SNAP)); pg.wait_for_timeout(400); b = h(pg.evaluate(SNAP))
    check("control: while playing, two snapshots 400 ms apart differ", a != b, "SEEN" if a != b else "NOT SEEN")
    pg.click("#pause"); pg.wait_for_timeout(100); a = h(pg.evaluate(SNAP)); pg.wait_for_timeout(600); b = h(pg.evaluate(SNAP))
    check("a real click on Pause freezes it pixel for pixel", a == b and not pg.evaluate("window.rain.playing") and pg.inner_text("#pause") == "Play")
    pg.click("#pause"); pg.wait_for_timeout(500); c = h(pg.evaluate(SNAP))
    check("Play moves it again", c != b and pg.evaluate("window.rain.playing"))
    pg.click("#pause")
    pg.focus("#rain"); pg.keyboard.press("End"); hi = pg.evaluate("window.rain.beads"); pg.keyboard.press("Home"); lo = pg.evaluate("window.rain.beads")
    check("rain slider by keyboard: heaviest has more drops than lightest", hi > lo and pg.evaluate("window.rain.rain") == 1, f"{hi} vs {lo}")
    before = h(pg.evaluate(SNAP)); pg.click("#seed"); after = h(pg.evaluate(SNAP))
    check("'Another street' changes the picture", before != after and pg.evaluate("window.rain.seed") == 8)
    pg.set_viewport_size({"width": 390, "height": 800})
    check("phone width: no sideways scroll", pg.evaluate("document.documentElement.scrollWidth - innerWidth") == 0)
    rm = ctx.new_page(); rm.emulate_media(reduced_motion="reduce"); rm.goto((D / "index.html").as_uri()); rm.wait_for_function("window.rain !== undefined")
    check("reduced motion: starts paused, with a Play button", not rm.evaluate("window.rain.playing") and rm.inner_text("#pause") == "Play")
    check("no JS errors", not errs, errs)
    ctx.close()
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)
