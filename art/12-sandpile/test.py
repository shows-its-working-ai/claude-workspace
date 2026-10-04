"""Sandpile: the page's settled pile for 4,096 grains == sandpile.py's (random-order toppling), cell for cell after
cropping both to the occupied box; total topples match; grains conserved at every slider value; phone 0; no errors."""
import json, sys
from pathlib import Path
import numpy as np
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D))
from sandpile import sweep
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def crop(a):
    r = np.where(a.any(1))[0]; c = np.where(a.any(0))[0]; return a[r[0]:r[-1] + 1, c[0]:c[-1] + 1]
py = np.array(json.loads((D / "sandpile4096.json").read_text(encoding="utf-8")))
_, pytop = sweep(4096, 81)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.sand !== undefined")
    pg.fill("#k", "12"); pg.dispatch_event("#k", "input"); pg.wait_for_function("window.sand && window.sand.N === 4096"); s = pg.evaluate("window.sand")
    js = np.array(s["grid"]).reshape(s["size"], s["size"])
    check("4,096 grains: page pile == Python pile, cell for cell", js.shape[0] > 0 and crop(js).shape == crop(py).shape and (crop(js) == crop(py)).all(),
          f"{crop(js).shape} vs {crop(py).shape}")
    check("4,096 grains: total topples equal", s["topples"] == int(pytop.sum()), f"{s['topples']} vs {int(pytop.sum())}")
    bad = []
    for kv in range(8, 18):
        pg.fill("#k", str(kv)); pg.dispatch_event("#k", "input"); pg.wait_for_function(f"window.sand && window.sand.N === {1 << kv}", timeout=60000); s = pg.evaluate("window.sand")
        g = np.array(s["grid"]).reshape(s["size"], s["size"])
        if s["grains"] != 1 << kv or g.max() > 3 or g[0].any() or g[-1].any() or g[:, 0].any() or g[:, -1].any(): bad.append(kv)
    check("every slider value: all grains kept, heights < 4, nothing reaches the border", not bad, str(bad))
    # cycle 140: the page must stay responsive while the biggest pile settles (it runs in a worker now)
    pg.fill("#k", "17"); pg.dispatch_event("#k", "input")
    gap = pg.evaluate("""() => new Promise(res => { let last = performance.now(), worst = 0, n = 0;
        const f = () => { const t = performance.now(); worst = Math.max(worst, t - last); last = t;
          if (++n < 60) requestAnimationFrame(f); else res(worst); }; requestAnimationFrame(f); })""")
    busy = "settling" in pg.inner_text("#facts")
    check("while 131,072 grains settle, the page keeps drawing frames (worst gap < 250 ms)", gap < 250 and busy, f"worst frame gap {gap:.0f} ms")
    pg.fill("#k", "10"); pg.dispatch_event("#k", "input"); pg.wait_for_function("window.sand && window.sand.N === 1024")
    check("a newer request wins (stale big pile not drawn over it)", pg.evaluate("window.sand.N") == 1024)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.fill("#k", "15"); pg.dispatch_event("#k", "input"); pg.wait_for_function("window.sand && window.sand.N === 32768")
    pg.set_viewport_size({"width": 900, "height": 1100}); pg.screenshot(path=str(D / "look.png"))
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
