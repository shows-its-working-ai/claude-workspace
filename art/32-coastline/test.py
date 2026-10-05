"""How Long Is a Coastline?: the page's divider walk == coast.py's, step for step, on all 9 rulers; REAL clicks on the
presets give exactly 300 * 3 * (4/3)^k km (the Koch formula, worked out here, not read from the page); the slider by
keyboard moves the ruler and adds a measurement; the note's D and finest length == coast.json; the map isn't blank;
control: a 60 km ruler (not a power of a third) is NOT given by the formula; phone width; no JS errors."""
import json, math, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
data = json.loads((D / "coast.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
formula = lambda k: 300 * 3 * (4 / 3) ** k
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.coast !== undefined")
    bad = []
    for r, n, L in data["rows"]:
        # cycle 252: this compared only walkUnits' steps and gap, so a page that dropped the gap from the LENGTH it
        # shows survived a mutant (every 1/3^k ruler has a gap of exactly 0). It now checks the page's own measure().
        steps, Lp = pg.evaluate("r => { const m = measure(r); return [m.steps, m.L]; }", r)
        if steps != n or abs(Lp - L) > 1e-9: bad.append((r, n, steps, Lp, L))
    check("page measure() == coast.py on all 9 rulers (steps and length)", not bad and len(data["rows"]) == 9, bad)
    for k in range(1, 6):
        pg.click(f'#presets button[data-k="{k}"]'); c = pg.evaluate("window.coast")
        check(f"preset 1/3^{k} of a side measures exactly 300*3*(4/3)^{k} = {formula(k):,.1f} km", abs(c["L"] - formula(k)) < 1e-6 and f"{round(formula(k)):,}" in pg.inner_text("#read"), f'{c["L"]:.4f}')
    before = pg.evaluate("window.coast")
    pg.focus("#r"); pg.keyboard.press("Home");
    for _ in range(40): pg.keyboard.press("ArrowRight")
    after = pg.evaluate("window.coast")
    # cycle 252: I first expected "the coast grows" here; at 83.9 km it measured 1,025 km, SHORTER than 1,200 at 100 km.
    # Lengths aren't monotonic between powers of a third; the page now says so, and this checks what's true.
    check("slider by keyboard: ruler shrinks from 100 km, the reading changes, a new dot is added", after["r"] < 100 and abs(after["L"] - before["L"]) > 1 and after["hist"] > before["hist"], f'{after["r"]:.2f} km -> {after["L"]:.0f}')
    check("...and the page says lengths aren't steady (84 km vs 100 km)", "isn't steady" in pg.inner_text("main") and after["L"] < formula(1), f'{after["L"]:.0f} < {formula(1):.0f}')
    # control: 60 km is 1/5 of a side, not a power of a third; the Koch formula must not describe it
    l60 = pg.evaluate("r => { const [n, g] = walkUnits(r); return (n * r + g) * 300; }", 60 / 300)
    near = min(abs(l60 - formula(k)) for k in range(0, 6))
    check("control: a 60 km ruler is NOT on the formula (it can tell the difference)", near > 50, f"{l60:.1f} km, nearest formula value {near:.1f} away")
    note = pg.inner_text("main")
    check("the note's D and finest length == coast.json", f"{data['D']:.3f}" in note and f"{min(data['rows'])[2] * 300:,.0f} km" in note)
    check("D is log4/log3 to within 0.03", abs(data["D"] - math.log(4) / math.log(3)) < 0.03, f"{data['D']:.4f}")
    ink = pg.evaluate("""() => { const c = document.getElementById('map'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n / (c.width * c.height); }""")
    check("the map is drawn (a real share of it is land)", 0.2 < ink < 0.9, f"{ink:.2f}")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone width: no sideways scroll", ov == 0, ov)
    check("no JS errors", not errs, errs)
    ctx.close()
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)
