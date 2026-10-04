"""Four Boxes: the page's value() == boxes.py's on all 4,096 positions; played by clicks: an outside opening + perfect
play wins 3-1; an inside opening ends in a 2-2 draw with perfect play; the computer starting wins 3-1 against perfect play;
every time the human's line closes a box, the human moves again (checked during those games); phone 0; no JS errors."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ns = {}; exec((D / "boxes.py").read_text(encoding="utf-8").split("v0 = value(0)")[0], ns)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
extra = {"closed": 0, "kept_turn": 0}
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.boxesApi !== undefined")
    js = pg.evaluate("[...Array(4096).keys()].map(m => boxesApi.value(m))")
    check("page value == Python on all 4,096 positions", js == [ns["value"](m) for m in range(4096)])
    def click(e):
        b = pg.evaluate("window.boxes"); k = ns["made"](b["mask"], e)
        pg.click(f".ln[data-e='{e}']", force=True)
        a = pg.evaluate("window.boxes")
        if k and not a["over"]: extra["closed"] += 1; extra["kept_turn"] += a["mover"] == 0
    def finish():
        for _ in range(30):
            b = pg.evaluate("window.boxes")
            if b["over"]: return b
            if b["mover"] == 0: click(pg.evaluate("m => boxesApi.bestMove(m)", b["mask"]))
            else: pg.wait_for_timeout(300)
        return pg.evaluate("window.boxes")
    pg.click("#new"); click(0); b = finish()
    check("outside opening + perfect play wins 3-1", b["scores"] == [3, 1], str(b["scores"]))
    pg.click("#new"); click(2); b = finish()
    check("inside opening: perfect play both ways ends 2-2", b["scores"] == [2, 2], str(b["scores"]))
    pg.click("#newc"); pg.wait_for_timeout(350); b = finish()
    check("computer starts: wins 3-1 against perfect play", b["scores"] == [1, 3], str(b["scores"]))
    check(f"every box the human closed mid-game ({extra['closed']}) kept the turn", extra["closed"] > 0 and extra["kept_turn"] == extra["closed"])
    check("note states the 2x3 result boxes23.py found", "on 2 by 3 boxes, the second player wins, 4 to 2" in pg.inner_text("main"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 700, "height": 900}); pg.screenshot(path=str(D.parents[1] / "tools" / "_boxes_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
