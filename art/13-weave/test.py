"""Weave: every swatch's colour grid == weave.py's, crossing for crossing (32 x 32, 4 drafts); phone overflow 0; no
JS errors. The Python side also checks plain = checkerboard, twill balance, houndstooth period 8."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "weave.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.weave !== undefined")
    js = pg.evaluate("window.weave")
    for name in py: check(f"{name}: page == Python, all 1,024 crossings", js.get(name) == py[name])
    # cycle 149: weave your own
    sys.path.insert(0, str(D)); from weave import drawdown, colours, DRAFTS
    m = pg.evaluate("window.mine")
    check("'weave your own' starts as houndstooth (== Python's houndstooth)", m["grid"] == py["houndstooth"] and m["warp"] == "00001111")
    pg.select_option("#kind", "plain")
    for i in (1, 3, 5, 7): pg.click(f"#warp button:nth-child({i + 1})")       # warp 00001111 -> 01011010
    for i in (0, 1): pg.click(f"#weft button:nth-child({i + 1})")             # weft 00001111 -> 11001111
    m = pg.evaluate("window.mine"); th, tu, tr, _, _ = DRAFTS["plain weave"]
    want = colours(drawdown(th, tu, tr, 32, 32), [0, 1, 0, 1, 1, 0, 1, 0], [1, 1, 0, 0, 1, 1, 1, 1])
    check("clicked design (plain, warp 01011010, weft 11001111) == Python, all 1,024 crossings",
          m["warp"] == "01011010" and m["weft"] == "11001111" and m["grid"] == want, f"{m['warp']} {m['weft']}")
    check("the address keeps the design", pg.evaluate("location.hash") == "#w=plain&warp=01011010&weft=11001111", pg.evaluate("location.hash"))
    pg.goto("about:blank"); pg.goto((D / "index.html").as_uri() + "#w=point&warp=11110000&weft=10101010"); pg.wait_for_function("window.mine !== undefined")
    m = pg.evaluate("window.mine"); th, tu, tr, _, _ = DRAFTS["chevron"]
    want = colours(drawdown(th, tu, tr, 32, 32), [1, 1, 1, 1, 0, 0, 0, 0], [1, 0, 1, 0, 1, 0, 1, 0])
    check("a shared link loads its design (point twill) == Python", m["w"] == "point" and m["grid"] == want and pg.input_value("#kind") == "point")
    pg.evaluate("location.hash = 'w=plain&warp=11111111&weft=00000000'"); pg.wait_for_timeout(200)
    check("a design link pasted into an open tab updates the cloth", pg.evaluate("window.mine.w") == "plain" and pg.evaluate("window.mine.warp") == "11111111")
    pg.goto("about:blank"); pg.goto((D / "index.html").as_uri() + "#w=nonsense&warp=12&weft=<b>"); pg.wait_for_function("window.mine !== undefined")
    check("a broken link falls back to the default, no errors", pg.evaluate("window.mine.w") == "twill" and pg.evaluate("window.mine.warp") == "00001111")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 900, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
