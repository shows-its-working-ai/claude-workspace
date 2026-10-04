"""Blue Line: the page's rows == Python's (writing/ringing_15.py's ringer, independent of the JS) for every method;
extent facts; strike schedule (one strike per bell per row, handstroke gap); rendered audio is audible and never
clips; phone overflow 0; no JS errors."""
import sys
from math import factorial
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools")); sys.path.insert(0, str(D.parents[1] / "writing"))
from ringing_15 import ring
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
EXPECT = {  # name: (stage, place notation, leads, distinct changes, is extent)
    "Plain Hunt Minimus": (4, ["x", "14"], 4, 8, False),
    "Plain Bob Minimus": (4, ["x", "14", "x", "14", "x", "14", "x", "12"], 3, 24, True),
    "The other one: x14x12x14x34": (4, ["x", "14", "x", "12", "x", "14", "x", "34"], 3, 24, True),
    "Plain Hunt Doubles": (5, ["5", "1"], 5, 10, False),
    "Plain Bob Doubles": (5, ["5", "1", "5", "1", "5", "1", "5", "1", "5", "125"], 4, 40, False),
}
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.bl !== undefined")
    for name, (st, pn, leads, distinct, extent) in EXPECT.items():
        start = "12345"[:st]
        py = [start] + ring(pn, leads, start)
        js = pg.evaluate(f"bl.rows({name!r})")
        check(f"{name}: JS rows == Python rows ({len(py) - 1} changes)", js == py)
        check(f"{name}: comes round, {distinct} distinct, extent={extent}",
              py[-1] == start and len(set(py[1:])) == distinct == len(py) - 1 and (distinct == factorial(st)) == extent)
        check(f"{name}: no bell moves more than one place", all(abs(a.index(b) - c.index(b)) <= 1 for a, c in zip(py, py[1:]) for b in start))
        sc = pg.evaluate(f"bl.schedule({name!r}, 0.2)")
        gaps = [round(b["t"] - a["t"], 6) for a, b in zip(sc, sc[1:])]
        want = [0.4 if (b["row"] != a["row"] and b["row"] % 2 == 0) else 0.2 for a, b in zip(sc, sc[1:])]
        check(f"{name}: {len(py) * st} strikes, one per bell per row, gap before each handstroke row",
              len(sc) == len(py) * st and all(abs(g - w) < 1e-6 for g, w in zip(gaps, want))
              and all("".join(str(s["bell"]) for s in sc if s["row"] == i) == r for i, r in enumerate(py)))
        pg.select_option("#method", name); pg.wait_for_timeout(100)
        txt = pg.inner_text("#facts")
        check(f"{name}: facts panel says {distinct} distinct" + (" and 'extent'" if extent else ""),
              f"{distinct} of them different" in txt and (("extent" in txt) == extent), txt[:90].replace("\n", " "))
    note = pg.inner_text("main")
    check("page text quotes the counts that extents.py and extents_dp.py produce (10,792 / 24 / two methods)",
          "10,792 ways" in note and "Only 24 of the 10,792" in note and "just two methods" in note)
    r = pg.evaluate("blRender('Plain Bob Doubles')")
    check("audio: 205 strikes rendered, audible (peak > 0.05) and never clipping (peak < 1)",
          r["strikes"] == 41 * 5 and 0.05 < r["peak"] < 1, f"peak={r['peak']:.3f}")
    pg.select_option("#method", "Plain Bob Minimus"); pg.wait_for_timeout(100)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 960, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
