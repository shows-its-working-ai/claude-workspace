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
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # labels like B-bar use combining marks
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser, shard
from playwright.sync_api import sync_playwright
MIN_FRACTION = 0.002
# Deliberately (near-)empty at load, each with its reason. Anything else blank is a bug.
ALLOW = {("projects/09-ant/index.html", 0): "starts as an empty grid on purpose; the ant is the only mark until Play"}
ONLY = sys.argv[1:]                                   # optional: check only these pages (used by the mutation test)
tracked = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
pages = ONLY or shard([f for f in tracked if f.endswith(".html") and "template" not in f])
MEASURE = """async ([a64, b64]) => {
  // fraction of pixels where the canvas (a) differs from an EMPTY copy of itself with identical CSS (b).
  // cycle 95, final design: b is the same canvas, same place, cleared; borders, corners, backgrounds and
  // anti-aliasing cancel out and only what it drew remains. (Rejected: reading the bitmap; counting colours; an
  // overlaid empty clone, which was transparent and so showed the original underneath.)
  const load = async s => { const i = new Image(); i.src = 'data:image/png;base64,' + s; await i.decode(); return i; };
  const [A, B] = [await load(a64), await load(b64)];
  if (A.width !== B.width || A.height !== B.height) return -1;
  const px = im => { const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
    const x = c.getContext('2d'); x.drawImage(im, 0, 0); return x.getImageData(0, 0, c.width, c.height).data; };
  const a = px(A), b = px(B); let diff = 0;
  for (let k = 0; k < a.length; k += 4) if (Math.abs(a[k] - b[k]) + Math.abs(a[k+1] - b[k+1]) + Math.abs(a[k+2] - b[k+2]) > 40) diff++;
  return diff / (a.length / 4);
}"""
blank, checked, hidden = [], 0, 0
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); pg.set_viewport_size({"width": 1000, "height": 900})
    pg.emulate_media(reduced_motion="reduce")       # animated pages pause, so nothing redraws between the two shots
    for f in pages:
        pg.goto((ROOT / f).as_uri()); pg.wait_for_timeout(1500)
        # freeze animation loops so nothing repaints between the drawn shot and the cleared (empty) shot
        pg.evaluate("window.requestAnimationFrame = () => 0"); pg.wait_for_timeout(150)
        canv = pg.locator("canvas")
        for i in range(canv.count()):
            el = canv.nth(i)
            box = el.bounding_box()
            if not box or box["width"] < 2 or box["height"] < 2 or not el.is_visible(): hidden += 1; continue
            el.scroll_into_view_if_needed()
            shot = el.screenshot()
            # the empty reference: the SAME canvas in the same place, its pixels saved, cleared, screenshotted, restored
            saved = el.evaluate("""c => { const x = c.getContext('2d'); if (!x) return false;
                window.__saved = x.getImageData(0, 0, c.width, c.height); x.clearRect(0, 0, c.width, c.height); return true; }""")
            if not saved: print(f"SKIP (no 2d context) {f} canvas {i}"); hidden += 1; continue
            ref = el.screenshot()
            el.evaluate("c => c.getContext('2d').putImageData(window.__saved, 0, 0)")
            frac = pg.evaluate(MEASURE, [base64.b64encode(shot).decode(), base64.b64encode(ref).decode()])
            if frac < 0: print(f"SIZE MISMATCH {f} canvas {i}"); blank.append((f, i)); continue
            checked += 1
            if frac >= MIN_FRACTION: continue
            if (f, i) in ALLOW: print(f"allowed {f} canvas {i}: {ALLOW[(f, i)]}"); continue
            blank.append((f, i)); print(f"BLANK {f} canvas {i} '{(el.get_attribute('aria-label') or '')[:50]}' visible-diff={frac:.5f}")
    ctx.close()
print(f"{len(pages)} pages, {checked} visible canvases checked, {hidden} hidden skipped, {len(blank)} blank")
print("CANVASES OK" if not blank else "BLANK CANVASES FOUND")
