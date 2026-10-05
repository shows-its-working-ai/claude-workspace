"""Collatz Coral: the page's step counts for 1..3,000 == collatz.py's; 27's caption (111 steps, 9,232) and 6171's
261 come from the page's own code; red appears ONLY when 27 is shown (control: none before); 2,999 paths drawn;
phone overflow 0; no JS errors."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
py = json.loads((D / "collatz.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
RED = """() => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    const h = getComputedStyle(document.documentElement).getPropertyValue('--hot').trim(), r = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
    let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - r[0]) < 8 && Math.abs(d[i + 1] - r[1]) < 8 && Math.abs(d[i + 2] - r[2]) < 8) n++; return n; }"""
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.coral !== undefined")
    js = pg.evaluate("[...Array(3000)].map((_, i) => coralApi.steps(i + 1))")
    check("page step counts 1..3,000 == collatz.py", js == py["steps_1_to_3000"])
    check("6171 takes 261 steps on the page", pg.evaluate("coralApi.steps(6171)") == py["longest_steps"] == 261)
    check("2,999 paths drawn at 3,000", pg.evaluate("coral.drawn") == 2999)
    before = pg.evaluate(RED); check("control: no red before 27 is shown", before == 0, f"{before}")
    pg.click("#t27"); after = pg.evaluate(RED)
    check("red appears when 27 is shown", after > 100, f"{after}")
    cap = pg.inner_text("#cap")
    check("caption: 27 takes 111 steps, as high as 9,232", "111 steps" in cap and "9,232" in cap and py["steps_27"] == 111 and py["peak_27"] == 9232, cap)
    pg.click("[data-n='500']"); check("500 button redraws 499 paths", pg.evaluate("coral.drawn") == 499 and pg.evaluate("coral.show27"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 900}); pg.click("[data-n='3000']")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_coral_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
