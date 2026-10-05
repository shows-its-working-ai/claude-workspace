"""Last Burn: the page's physics == lander.py's, step for step, for the autopilot and 3 scripted burn patterns; the
autopilot flown IN REAL TIME on the page lands softly on exactly lander.py's fuel; a REAL held space bar and a REAL
held mouse button burn for about as long as they're held; control: no burn = a crash, reported as one; 'New landing'
during the autopilot's flight stops it (no stale frames); phone 0; no JS errors."""
import json, sys, time
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "lander.json").read_text(encoding="utf-8"))
ns = {"__file__": str(D / "lander.py")}; exec((D / "lander.py").read_text(encoding="utf-8").split("r = fly(suicide)")[0], ns)
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
pats = [[k < 300 for k in range(2000)], [600 <= k < 1100 for k in range(2000)], [(k // 50) % 2 == 0 for k in range(2000)]]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.landerApi !== undefined")
    a = pg.evaluate("landerApi.fly((k, h, v) => landerApi.autopilot(h, v))")
    check("page autopilot == lander.py, exactly", a["v"] == py["suicide"]["v"] and a["fuel"] == py["suicide"]["fuel"] and a["steps"] == py["suicide"]["steps"], f"{a}")
    for i, pat in enumerate(pats):
        js = pg.evaluate("b => landerApi.fly(b)", pat); pr = ns["fly"](lambda k, h, v, P=pat: P[k] if k < len(P) else False)
        check(f"scripted burn pattern {i}: page == Python (speed, fuel, steps)", js["v"] == pr["v"] and js["fuel"] == pr["fuel"] and js["steps"] == pr["steps"])
    pg.click("#auto"); t0 = time.time(); pg.wait_for_function("window.lander && window.lander.done", timeout=40000)
    L = pg.evaluate("window.lander")
    check("autopilot in REAL TIME lands softly on lander.py's exact fuel", L["soft"] and L["fuelS"] == py["suicide"]["fuel"] and "Landed at 1.99" in pg.inner_text("#msg"), f"{L['fuelS']} in {time.time() - t0:.1f}s")
    # real input: hold space ~1 s, then hold the mouse on the button ~0.6 s
    pg.click("#go"); pg.wait_for_timeout(200); pg.keyboard.down("Space"); pg.wait_for_timeout(1000); pg.keyboard.up("Space")
    f1 = pg.evaluate("window.lander.fuel") / 120
    check("real held space bar ~1 s burns ~1 s", 0.8 <= f1 <= 1.25, f"{f1:.2f} s")
    b = pg.locator("#burn").bounding_box(); pg.mouse.move(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
    pg.mouse.down(); pg.wait_for_timeout(600); pg.mouse.up(); pg.wait_for_timeout(100)
    f2 = pg.evaluate("window.lander.fuel") / 120 - f1
    check("real held mouse button ~0.6 s burns ~0.6 s, and stops on release", 0.45 <= f2 <= 0.8 and pg.evaluate("window.lander.on") is False, f"{f2:.2f} s")
    pg.wait_for_function("window.lander.done", timeout=40000)
    check("control: a weak burn crashes, and the page says so", not pg.evaluate("window.lander.soft") and "Crashed" in pg.inner_text("#msg"))
    pg.click("#auto"); pg.wait_for_timeout(300); pg.click("#go"); pg.wait_for_timeout(1500)
    check("New landing during the autopilot stops it (no stale burning)", pg.evaluate("window.lander.pilot") is False and pg.evaluate("window.lander.fuel") == 0)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 1000}); pg.wait_for_timeout(2500)
    pg.screenshot(path=str(D.parents[1] / "tools" / "_lander_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
