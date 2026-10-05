"""Mirror Sketch: draws REAL strokes (mouse at desktop, touchscreen at phone width) and measures the PIXELS:
(a) n-fold rotational symmetry: for sampled ink pixels, the pixel rotated by 360/n is also ink (within 2 px);
(b) mirror on: also symmetric under y -> -y about the centre; control: mirror OFF with a lopsided stroke is NOT;
(c) undo removes exactly the last stroke; clear empties the canvas; (d) no network request; Save makes a PNG download;
(e) a stroke keeps the copies it was drawn with when n is changed later; phone 0; no JS errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser, open_touch
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
SYM = """([n, mode]) => { const c = document.getElementById('cv'), S = c.width, C = S / 2, d = c.getContext('2d').getImageData(0, 0, S, S).data;
  const ink = (x, y) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= S || y >= S) return false;
    const i = 4 * (y * S + x); return d[i] + d[i + 1] + d[i + 2] < 600; };
  const near = (x, y) => { for (let dx = -2; dx <= 2; dx++) for (let dy = -2; dy <= 2; dy++) if (ink(x + dx, y + dy)) return true; return false; };
  let tot = 0, hit = 0;
  for (let y = 0; y < S; y += 3) for (let x = 0; x < S; x += 3){ if (!ink(x, y)) continue; const px = x - C, py = y - C;
    let qx, qy; if (mode === 'rot'){ const a = 2 * Math.PI / n; qx = px * Math.cos(a) - py * Math.sin(a); qy = px * Math.sin(a) + py * Math.cos(a); } else { qx = px; qy = -py; }
    tot++; if (near(qx + C, qy + C)) hit++; }
  return [tot, tot ? hit / tot : 0]; }"""
def drag(pg, pts, touch=False):
    b = pg.locator("#cv").bounding_box(); P = [(b["x"] + x * b["width"], b["y"] + y * b["height"]) for x, y in pts]
    if touch:   # a real touch drag via CDP touch events
        cdp = pg.context.new_cdp_session(pg)
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": P[0][0], "y": P[0][1]}]})
        for x, y in P[1:]: cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x, "y": y}]})
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); return
    pg.mouse.move(*P[0]); pg.mouse.down()
    for x, y in P[1:]: pg.mouse.move(x, y, steps=4)
    pg.mouse.up()
LOP = [(0.55, 0.30), (0.62, 0.35), (0.70, 0.33), (0.78, 0.40), (0.80, 0.44)]   # off-centre, not symmetric about the x axis
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; reqs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); ctx.on("request", lambda r: reqs.append(r.url))   # the whole context: the Save step runs on a second page
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.sketch !== undefined"); reqs.clear()
    pg.evaluate("document.getElementById('cv').scrollIntoView({block: 'center'})")
    s0 = pg.evaluate("window.sketch"); tot0, f0 = pg.evaluate(SYM, [6, "rot"])
    check("the page opens with a 6-fold example (not a blank square)", s0["strokes"] == 2 and tot0 > 200 and f0 > 0.97, f"{tot0} ink samples")
    for n in (6, 5):
        pg.click("#clear"); pg.select_option("#n", str(n)); drag(pg, LOP)
        tot, f = pg.evaluate(SYM, [n, "rot"]); check(f"(a) {n} copies: ink matches when turned 360/{n} degrees", tot > 200 and f > 0.97, f"{f:.3f} of {tot}")
        tot, m = pg.evaluate(SYM, [n, "mir"]); check(f"(b) mirror on: also mirror-symmetric", m > 0.97, f"{m:.3f}")
    pg.click("#clear"); pg.click("#mirror"); pg.select_option("#n", "5"); drag(pg, LOP)
    _, f = pg.evaluate(SYM, [5, "rot"]); _, m = pg.evaluate(SYM, [5, "mir"])
    check("control: mirror OFF + lopsided stroke: still rotation-symmetric, NOT mirror-symmetric", f > 0.97 and m < 0.6, f"rot {f:.3f}, mirror {m:.3f}")
    pg.click("#mirror")
    pg.select_option("#n", "8"); drag(pg, [(0.5, 0.75), (0.55, 0.8)]); s = pg.evaluate("window.sketch")
    _, f5 = pg.evaluate(SYM, [5, "rot"]); _, f8 = pg.evaluate(SYM, [8, "rot"])
    # if changing n had redrawn the FIRST stroke with 8 copies too, the picture would be fully 8-fold
    check("(e) the earlier stroke keeps its 5 copies: the picture is neither 5-fold nor 8-fold", s["strokes"] == 2 and f5 < 0.97 and f8 < 0.97, f"5-fold {f5:.3f}, 8-fold {f8:.3f}")
    pg.click("#undo"); _, f = pg.evaluate(SYM, [5, "rot"])
    check("(c) undo removes exactly the last stroke (back to 5-fold)", pg.evaluate("sketch.strokes") == 1 and f > 0.97)
    pg.click("#clear"); tot, _ = pg.evaluate(SYM, [5, "rot"])
    check("(c) clear empties the canvas", pg.evaluate("sketch.strokes") == 0 and tot == 0)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 1100}); pg.click("#clear"); pg.select_option("#n", "8"); pg.click("#colours button:nth-child(3)")
    drag(pg, [(0.5, 0.2), (0.58, 0.28), (0.62, 0.4), (0.56, 0.45)]); pg.click("#colours button:nth-child(2)"); drag(pg, [(0.5, 0.35), (0.53, 0.32), (0.55, 0.36)])
    pg.screenshot(path=str(D.parents[1] / "tools" / "_kaleido_look.png"), full_page=True)
    pg = ctx.new_page(); pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.sketch !== undefined")   # download last, on its own page
    pg.evaluate("document.getElementById('cv').scrollIntoView({block: 'center'})")
    drag(pg, LOP)
    with pg.expect_download() as dl: pg.click("#save")
    import base64   # cycle 242: reading dl.path() was flaky ("context closed"); the download URL IS the PNG (a data: URL)
    name = dl.value.suggested_filename; url = dl.value.url
    head = base64.b64decode(url.split(",", 1)[1])[:8] if url.startswith("data:image/png;base64,") else b""
    check("(d) Save gives a PNG download", name == "mirror-sketch.png" and head == b"\x89PNG\r\n\x1a\n")
    check("(d) no network request at all, Save included (only the page files themselves)", [r for r in reqs if not r.startswith(("data:", "file:"))] == [], str([r for r in reqs if not r.startswith(("data:", "file:"))][:3]))
    ctx.close()
    tc = open_touch(p); tp = tc.new_page(); tp.goto((D / "index.html").as_uri()); tp.wait_for_function("window.sketch !== undefined")
    tp.evaluate("document.getElementById('cv').scrollIntoView({block: 'center'})"); tp.click("#clear"); drag(tp, LOP, touch=True)
    tot, f = tp.evaluate(SYM, [6, "rot"])
    check("real touchscreen drag at phone width draws a 6-fold stroke", tp.evaluate("sketch.strokes") == 1 and tot > 50 and f > 0.95, f"{f:.3f} of {tot}")
    tc.close()
print("ALL PASS" if ok else "FAILURES")
