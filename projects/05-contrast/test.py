"""Contrast tool checks: (1) reference values 21 and 4.54; (2) JS ratio == my Python ratio (tools/contrast.py,
validated in cycle 25) on 500 random pairs; (3) every suggested fix PASSES 4.5 and keeps hue (non-grey); (4) the
page: default example shows 3.13 and a fix; 'Use it' applies a passing colour; keyboard, phone width, no errors."""
import random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from contrast import ratio as py_ratio
from playwright.sync_api import sync_playwright
rng = random.Random(51); ok = True
hexs = lambda: "#%06x" % rng.randrange(0x1000000)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    r1 = pg.evaluate("ratio(hexToRgb('#000000'), hexToRgb('#ffffff'))"); r2 = pg.evaluate("ratio(hexToRgb('#767676'), hexToRgb('#ffffff'))")
    refs = abs(r1 - 21) < 1e-9 and round(r2, 2) == 4.54; ok &= refs
    print(f"(1) reference values: black/white {r1:.4f}, #767676/white {r2:.4f} -> {'ok' if refs else 'FAIL'}")
    pairs = [(hexs(), hexs()) for _ in range(500)]
    js = pg.evaluate("ps => ps.map(([a, b]) => ratio(hexToRgb(a), hexToRgb(b)))", pairs)
    worst = max(abs(j - py_ratio(a, b)) for j, (a, b) in zip(js, pairs)); ok &= worst < 1e-9
    print(f"(2) JS vs Python ratio on 500 random pairs: max difference {worst:.2e}")
    failing = [(a, b) for (a, b), j in zip(pairs, js) if j < 4.5][:300]
    res = pg.evaluate("""ps => ps.map(([a, b]) => { const s = suggest(hexToRgb(a), hexToRgb(b));
        return [toHex(s), ratio(s, hexToRgb(b)), rgbToHsl(hexToRgb(a)), rgbToHsl(s)]; })""", failing)
    passes = sum(r >= 4.5 for _, r, _, _ in res)
    # Hue must be kept, EXCEPT when the only passing colour is near-black/white (L<.03 or >.97), where hue is
    # meaningless after 8-bit rounding; in exactly those cases the page must SAY so (checked below).
    extreme = [i for i, (_, _, h0, h1) in enumerate(res) if h1[2] < 0.03 or h1[2] > 0.97]
    huekept = sum(1 for i, (_, _, h0, h1) in enumerate(res) if i in extreme or h0[1] < 0.15 or
                  min(abs(h0[0] - h1[0]), 1 - abs(h0[0] - h1[0])) < 0.03)
    print(f"(3) suggestions for {len(failing)} failing pairs: {passes} pass 4.5:1; hue kept on {huekept} "
          f"({len(extreme)} near-black/white, where hue can't apply)")
    ok &= passes == len(failing) and huekept == len(failing)
    said = 0
    for i in extreme:
        a_, b_ = failing[i]; pg.fill("#fgt", a_); pg.fill("#bgt", b_); said += pg.locator("#extreme").count()
    plain = [i for i in range(len(res)) if i not in extreme][:20]; wrongly = 0
    for i in plain:
        a_, b_ = failing[i]; pg.fill("#fgt", a_); pg.fill("#bgt", b_); wrongly += pg.locator("#extreme").count()
    print(f"    page says 'only near-black/white passes' on {said}/{len(extreme)} extreme cases, and wrongly on {wrongly}/{len(plain)} normal ones")
    ok &= said == len(extreme) and wrongly == 0
    pg.fill("#fgt", "#8a8278"); pg.fill("#bgt", "#efe9dd")
    page_ratio = pg.inner_text("#ratio"); has_fix = pg.locator("#use").count() == 1
    pg.focus("#use"); pg.keyboard.press("Enter")
    after = float(pg.evaluate("document.body.dataset.ratio")); passed_msg = "Passes AA" in pg.inner_text("#fix")
    print(f"(4) default example shows {page_ratio!r}, fix offered: {has_fix}; after 'Use it' (keyboard): {after:.2f}, passes: {passed_msg}")
    ok &= page_ratio.startswith("3.13") and has_fix and after >= 4.5 and passed_msg
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth"); print("phone overflow:", ov, "| js errors:", errs)
    ok &= ov == 0 and not errs
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
