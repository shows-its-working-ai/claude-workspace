"""Quiet Patterns: the page's symmetric quiet patterns (computed in JS) must equal quiet.py's exactly, size by size;
every one must be quiet; 28 panels + 6 turning ones; phone overflow 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
py = json.loads((D / "quiet.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.quiet !== undefined", timeout=60000)
    js = pg.evaluate("window.quiet")
    for n, rec in py.items():
        got = js["result"][n]
        check(f"n={n}: nullity {rec['nullity']} and {len(rec['fully_symmetric'])} symmetric patterns, same as Python",
              got["nullity"] == rec["nullity"] and sorted(got["symmetric"]) == sorted(rec["fully_symmetric"]))
    check("every displayed pattern is quiet (checked in the page)", js["allQuiet"] and js["total"] == 28, f"total {js['total']}")
    check("34 panels on the page (28 + 6 turning)", pg.locator("figure").count() == 34)
    tu = pg.evaluate("window.turned"); chiral = {(m, n) for m, n, _, _ in json.loads((D / 'rect.json').read_text(encoding='utf-8'))["found"]}
    check("6 turning patterns: each quiet, half-turn symmetric, NOT mirror symmetric",
          len(tu) == 6 and all(t["found"] and t["quiet"] and t["halfTurn"] and not t["mirrored"] for t in tu), str(tu)[:200])
    check("every turning board is one rect.py lists as half-turn-only", all((t["m"], t["n"]) in chiral for t in tu))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    pg.set_viewport_size({"width": 960, "height": 900}); pg.screenshot(path=str(D / "look.png"), full_page=True)
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
