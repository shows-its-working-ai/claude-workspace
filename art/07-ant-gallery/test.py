"""Eleven Ants: the page's own highway detection (JS, 50,000 steps) must equal the Python survey for every panel
(period and onset, or 'none'); 11 panels = one per mirror pair; the note names exactly LLLR and LLR; phone 0; no errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
survey = {s["rule"]: s for s in json.loads((D / "survey.json").read_text(encoding="utf-8"))}
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.gallery !== undefined", timeout=30000)
    g = pg.evaluate("window.gallery")
    check("11 panels, one per mirror pair", len(g["reps"]) == 11 and pg.locator("figure").count() == 11)
    for r in g["reps"]:
        s, js = survey[r], g["out"][r]
        same = (js is None and not s["highway"]) or (js is not None and s["highway"] and js["period"] == s["period"] and js["onset"] == s["onset"])
        check(f"{r}: page {js} == survey {('period %d onset %d' % (s['period'], s['onset'])) if s['highway'] else 'none'}", same)
    note = pg.inner_text("#note")
    check("note names exactly LLLR and LLR as the new highways", "Only 2 of these" in note and ("LLR and LLLR" in note or "LLLR and LLR" in note), note[:80])
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 960, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
