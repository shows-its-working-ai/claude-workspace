"""A Day in a Minute: tests only the MECHANICS (the beauty can't be tested):
(a) sky brightness from the CANVAS pixels: noon > dawn > midnight; (b) stars counted as pixels: present at 02:00,
none at 12:00; (c) same seed + time -> identical pixels, a different seed -> different hills; (d) Pause stops time;
REAL keyboard on the slider sets it; prefers-reduced-motion starts paused; the clock text follows the time;
control for (b): the star check sees stars on a night it should (so 'none at noon' isn't blind); phone 0; no errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
SKY = """() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, 120).data; let s = 0;
  for (let i = 0; i < d.length; i += 4) s += d[i] + d[i + 1] + d[i + 2]; return s / (d.length / 4) / 3; }"""
STARS = """() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, Math.floor(c.height * 0.45)).data; let n = 0;
  for (let i = 0; i < d.length; i += 4) if (d[i] === 255 && d[i + 1] === 255 && d[i + 2] === 240) n++; return n; }"""
SNAP = "() => { const d = document.getElementById('cv').getContext('2d').getImageData(0, 0, 960, 540).data; let h = 0; for (let i = 0; i < d.length; i += 97) h = (h * 31 + d[i]) >>> 0; return h; }"
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.day !== undefined"); pg.evaluate("dayApi.pause()")
    b = {}
    for name, m in (("midnight", 0), ("dawn", 400), ("noon", 720)):
        pg.evaluate(f"dayApi.set({m}, 5)"); b[name] = pg.evaluate(SKY)
    check("(a) sky brightness from pixels: noon > dawn > midnight", b["noon"] > b["dawn"] > b["midnight"], str({k: round(v) for k, v in b.items()}))
    pg.evaluate("dayApi.set(120, 5)"); s_night = pg.evaluate(STARS); pg.evaluate("dayApi.set(720, 5)"); s_noon = pg.evaluate(STARS)
    check("control: stars are seen at 02:00", s_night > 50, str(s_night))
    check("(b) no stars at noon", s_noon == 0, str(s_noon))
    pg.evaluate("dayApi.set(1110, 5)"); h1 = pg.evaluate(SNAP); pg.evaluate("dayApi.set(600, 9)"); pg.evaluate("dayApi.set(1110, 5)"); h2 = pg.evaluate(SNAP)
    pg.evaluate("dayApi.set(1110, 6)"); h3 = pg.evaluate(SNAP)
    check("(c) same seed and time draw identical pixels; another seed differs", h1 == h2 and h1 != h3)
    pg.evaluate("dayApi.set(500, 5)"); m0 = pg.evaluate("day.minute"); pg.wait_for_timeout(600)
    check("(d) paused: time doesn't move", pg.evaluate("day.minute") == m0)
    pg.click("#pause"); pg.wait_for_timeout(600); m1 = pg.evaluate("day.minute")
    check("Play: time moves about 24 minutes a second", 6 <= m1 - m0 <= 20, f"{m1 - m0:.1f} min in 0.6 s")
    pg.click("#pause"); pg.focus("#t"); pg.keyboard.press("Home"); pg.keyboard.press("ArrowRight")
    check("real keyboard on the slider sets the time; clock reads 00:01", pg.evaluate("day.minute") == 1 and pg.inner_text("#clock") == "00:01")
    ctx.close()
    from mybrowser import CHROME
    b2 = p.chromium.launch(executable_path=str(CHROME)); c2 = b2.new_context(reduced_motion="reduce"); q = c2.new_page()
    q.goto((D / "index.html").as_uri()); q.wait_for_function("window.day !== undefined"); m0 = q.evaluate("day.minute"); q.wait_for_timeout(500)
    check("prefers-reduced-motion: starts paused", q.evaluate("day.playing") is False and q.evaluate("day.minute") == m0 and q.inner_text("#pause") == "Play")
    q.set_viewport_size({"width": 390, "height": 800})
    ov = q.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    q.set_viewport_size({"width": 800, "height": 900}); q.evaluate("dayApi.set(1100, 3)")
    q.screenshot(path=str(D.parents[1] / "tools" / "_day_look.png"), full_page=True); b2.close()
print("ALL PASS" if ok else "FAILURES")
