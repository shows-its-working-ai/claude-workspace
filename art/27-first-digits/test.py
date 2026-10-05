"""First Digits: the page's snapshot == digits.json (the committed --snapshot); the drawn bars' heights are
proportional to the shares and the dots sit at Benford's log10(1 + 1/d); the note's numbers come from the snapshot;
control: the page counts ITSELF out (digits.py excludes this folder); phone 0; no JS errors."""
import json, math, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "digits.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.digits !== undefined")
    S = pg.evaluate("digits.SNAP")
    check("page snapshot == digits.json", all(S[k] == py[k] for k in ("cycle", "pages", "n", "big", "big1", "r110", "years", "observed")) and S["chi"] == round(py["chi"], 2))
    hs = pg.evaluate("[...document.querySelectorAll('#chart rect')].map(r => +r.getAttribute('height'))")
    sh = [o / py["n"] for o in py["observed"]]
    check("9 bars, heights proportional to the shares", len(hs) == 9 and all(abs(h / hs[0] - s / sh[0]) < 1e-9 for h, s in zip(hs, sh)))
    cy = pg.evaluate("[...document.querySelectorAll('#chart circle')].map(c => +c.getAttribute('cy'))")
    check("dots at Benford's log10(1 + 1/d)", all(abs(c - (260 - math.log10(1 + 1 / d) / 0.45 * 230)) < 1e-9 for d, c in zip(range(1, 10), cy)))
    note = pg.inner_text("#note")
    check("note: numbers from the snapshot", f"{py['n']:,} numbers on {py['pages']} pages" in note and f"{100 * py['observed'][0] / py['n']:.1f}%" in note
          and f"{100 * py['big1'] / py['big']:.1f}%" in note and f"appears {py['r110']} times" in note)
    src = (D / "digits.py").read_text(encoding="utf-8")
    check("control: digits.py excludes this page from its own count", '"27-first-digits" not in f' in src)
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 1000}); pg.screenshot(path=str(D.parents[1] / "tools" / "_digits_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
