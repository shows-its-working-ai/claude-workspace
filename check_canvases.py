"""Site-wide blank-canvas check (cycle 92). Twice a data test passed while the picture was empty: the Slide map drawn
under the tiles (cycle 72) and the blank LLR panel in Eleven Ants (cycle 91).
For every visible <canvas> on every public page this takes a SCREENSHOT of the canvas as displayed (so CSS scaling,
covering elements and pixelated down-sampling all count: what the user sees, not the canvas's internal bitmap),
decodes it in the browser, and measures the fraction of pixels that differ noticeably (colour distance > 40) from
the screenshot's most common colour. Below MIN_FRACTION = BLANK.
v1 of this check read the internal bitmap and MISSED the cycle-91 bug in a mutation test (the road was 0.3% of a
huge bitmap but vanished when scaled down); hence screenshots.
Prediction (written first, for v1): the current site has 0 blank canvases. (v1 found one, intentional; see ALLOW.)"""
import base64, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
MIN_FRACTION = 0.002
# Deliberately (near-)empty at load, each with its reason. Anything else blank is a bug.
ALLOW = {("projects/09-ant/index.html", 0): "starts as an empty grid on purpose; the ant is the only mark until Play"}
ONLY = sys.argv[1:]                                   # optional: check only these pages (used by the mutation test)
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
pages = ONLY or [f for f in tracked if f.endswith(".html") and "template" not in f]
MEASURE = """async (b64) => {
  const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
  const x = c.getContext('2d'); x.drawImage(img, 0, 0); const d = x.getImageData(0, 0, c.width, c.height).data;
  const counts = new Map();
  for (let k = 0; k < d.length; k += 4){ const key = d[k] << 16 | d[k+1] << 8 | d[k+2]; counts.set(key, (counts.get(key) || 0) + 1); }
  let topKey = 0, top = -1; for (const [k, v] of counts) if (v > top){ top = v; topKey = k; }
  const tr = topKey >> 16 & 255, tg = topKey >> 8 & 255, tb = topKey & 255; let diff = 0;
  for (let k = 0; k < d.length; k += 4) if (Math.abs(d[k] - tr) + Math.abs(d[k+1] - tg) + Math.abs(d[k+2] - tb) > 40) diff++;
  return diff / (d.length / 4);
}"""
blank, checked, hidden = [], 0, 0
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.set_viewport_size({"width": 1000, "height": 900})
    for f in pages:
        pg.goto((ROOT / f).as_uri()); pg.wait_for_timeout(1500)
        canv = pg.locator("canvas")
        for i in range(canv.count()):
            el = canv.nth(i)
            box = el.bounding_box()
            if not box or box["width"] < 2 or box["height"] < 2 or not el.is_visible(): hidden += 1; continue
            el.scroll_into_view_if_needed()
            frac = pg.evaluate(MEASURE, base64.b64encode(el.screenshot()).decode())
            checked += 1
            if frac >= MIN_FRACTION: continue
            if (f, i) in ALLOW: print(f"allowed {f} canvas {i}: {ALLOW[(f, i)]}"); continue
            blank.append((f, i)); print(f"BLANK {f} canvas {i} '{(el.get_attribute('aria-label') or '')[:50]}' visible-diff={frac:.5f}")
    ctx.close()
print(f"{len(pages)} pages, {checked} visible canvases checked, {hidden} hidden skipped, {len(blank)} blank")
print("CANVASES OK" if not blank else "BLANK CANVASES FOUND")
