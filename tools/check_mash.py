"""Button masher (cycle 202). Three bugs readers found (GitHub issues #1-#3) came from doing things in an order my
tests never tried: pressing a button twice, mashing New game. For every public page: 60 seeded random actions
(click a visible enabled button / [role=button], change a <select>, set range / number / text / colour inputs and
checkboxes, tap canvases and SVGs at random points), never following real
links; then the page must still answer. Fails on any JS error. Usage: check_mash.py [page ...]"""
import random, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
files = sys.argv[1:] or sorted(f for f in subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.html"],
        cwd=ROOT, capture_output=True, text=True).stdout.split() if (f.startswith("projects/") or f.startswith("art/")) and f.endswith("index.html"))
PICK = """(i) => { const els = [...document.querySelectorAll('button, [role=button], select, input[type=range], input[type=number], input[type=text], input[type=color], input[type=checkbox], canvas, svg')]
  .filter(e => !e.disabled && e.offsetParent !== null && !(e.tagName === 'A' && e.getAttribute('href') && e.getAttribute('href') !== '#'));
  if (!els.length) return null; const e = els[i % els.length];
  if (e.tagName === 'SELECT'){ e.selectedIndex = (e.selectedIndex + 1 + i) % e.options.length; e.dispatchEvent(new Event('change', {bubbles: true})); e.dispatchEvent(new Event('input', {bubbles: true})); return 'select'; }
  if (e.type === 'range'){ const lo = +e.min || 0, hi = +e.max || 100; e.value = lo + (i * 7919) % (hi - lo + 1); e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); return 'range'; }
  if (e.type === 'number' || e.type === 'text'){ e.value = e.type === 'number' ? String((i % 50) - 5) : ['', 'abc', '#123456', '999999'][i % 4]; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); return 'input'; }
  if (e.type === 'color'){ e.value = '#' + ((i * 2654435761) >>> 8 & 0xffffff).toString(16).padStart(6, '0'); e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); return 'color'; }
  if (e.tagName === 'CANVAS' || e.tagName === 'svg'){ const r = e.getBoundingClientRect(), x = r.left + (i % 97) / 97 * r.width, y = r.top + (i % 89) / 89 * r.height;
    const tgt = document.elementFromPoint(x, y) || e;                        // the shape actually under that point, if any
    for (const t of ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) tgt.dispatchEvent(new MouseEvent(t, {bubbles: true, cancelable: true, clientX: x, clientY: y}));
    return 'tap'; }
  e.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true})); return e.tagName.toLowerCase(); }"""
bad = []
with sync_playwright() as p:
    ctx = open_browser(p)
    for f in files:
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)[:160]))
        pg.on("dialog", lambda d: d.dismiss())
        # never leave the page: cancel clicks on real links (All 88's panels link to the Rule Explorer)
        pg.add_init_script("document.addEventListener('click', e => { const a = e.target.closest && e.target.closest('a[href]'); if (a && !a.getAttribute('href').startsWith('#')) e.preventDefault(); }, true);")
        url = (ROOT / f).as_uri(); pg.goto(url); pg.wait_for_timeout(300)
        rng = random.Random(f); acts = 0
        for _ in range(60):
            if pg.url.split("#")[0] != url: pg.goto(url); pg.wait_for_timeout(200)
            try:
                if pg.evaluate(PICK, rng.randrange(10 ** 6)): acts += 1
            except Exception as e:
                if "context was destroyed" in str(e) or "navigation" in str(e):        # a tap followed a link: fine, go back
                    pg.goto(url); pg.wait_for_timeout(200); continue
                errs.append("evaluate failed: " + str(e)[:120]); break
            pg.wait_for_timeout(rng.choice((0, 0, 10, 40)))
        pg.wait_for_timeout(400)
        try: alive = pg.evaluate("1 + 1") == 2
        except Exception: alive = False
        if errs or not alive: bad.append(f); print(f"FAIL {f}: {acts} actions; alive={alive}; errors: {errs[:3]}")
        else: print(f"ok   {f}: {acts} actions")
        pg.close()
    ctx.close()
print(f"{len(files)} pages mashed; {len(bad)} with errors")
print("MASH OK" if not bad else "MASH FAILED")
