"""Folded Poem: tests the MECHANICS honestly (the poetry can't be tested):
(a) while folded, the visible text shows the latest line and NONE of the earlier ones (checked after every fold);
(b) unfolded, every line is there in order, you and me alternating; (c) my lines come from a bank of 40 distinct
lines, none repeated in a poem; (d) no network request is made, even when Copy is pressed; (e) typed HTML shows as
text; (f) the chance two poems share one of my lines, sampled with the page's own picker, ~ 1 - C(36,4)/C(40,4)
(0.3555); control for (a): after unfolding, the earlier lines DO appear (so the 'not visible' check can see)."""
import sys
from math import comb
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
MY = ["a heron stood in the car park", "and I forgot the shopping list", "the moon was mostly a rumour", "<b>bold</b> & <i>brave</i>"]
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; reqs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("request", lambda r: reqs.append(r.url))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.folded !== undefined"); reqs.clear()
    bank = pg.evaluate("foldedApi.MINE")
    check("my bank: 40 lines, all different", len(bank) == 40 and len(set(bank)) == 40)
    seen, folded_ok = [], True
    for k, line in enumerate(MY):
        pg.click("#line"); pg.keyboard.type(line); pg.keyboard.press("Enter")
        s = pg.evaluate("window.folded"); seen.append(line)
        if s["done"]: break
        mine = bank[s["mineIdx"][-1]]; seen.append(mine)
        vis = pg.inner_text(".paper")
        if mine not in vis or any(old in vis for old in seen[:-1]): folded_ok = False; print("   leak after fold", k, repr(vis[:80]))
    check("(a) after every fold only the latest line is visible (3 checks, by real typing)", folded_ok)
    s = pg.evaluate("window.folded")
    check("unfolds by itself after 8 lines", s["done"] and s["count"] == 8)
    poem = pg.evaluate("[...document.querySelectorAll('#poem p')].map(p => p.textContent)")
    want = [x for i in range(4) for x in (MY[i], bank[s["mineIdx"][i]])]
    check("(b) unfolded: all 8 lines in order, you and me alternating", poem == want and s["who"] == ["you", "me"] * 4)
    check("control for (a): unfolded, the earlier lines ARE visible", all(x in pg.inner_text(".paper") for x in want))
    check("(c) my 4 lines are distinct bank lines", len(set(s["mineIdx"])) == 4)
    check("(e) typed HTML is shown as text, not markup", "<b>bold</b> & <i>brave</i>" in pg.inner_text("#poem") and pg.locator("#poem b, #poem i").count() == 0)
    pg.click("#copy"); pg.wait_for_timeout(300)
    check("(d) no network request at all, including Copy", reqs == [], str(reqs))
    p_hat = pg.evaluate("""(() => { let hit = 0, N = 20000; const draw = () => { const s = new Set(); for (let k = 0; k < 4; k++) foldedApi.pickMine(s); return s; };   // the PAGE's own picker
        for (let t = 0; t < N; t++){ const a = draw(), b = draw(); if ([...a].some(x => b.has(x))) hit++; } return hit / N; })()""")
    exact = 1 - comb(36, 4) / comb(40, 4)
    check("(f) chance two poems share one of my lines ~ 0.3555 (sampled 20,000)", abs(p_hat - exact) < 0.02, f"{p_hat:.4f} vs {exact:.4f}")
    pg.click("#again"); pg.click("#line"); pg.keyboard.type("one"); pg.keyboard.press("Enter"); pg.click("#unfold")
    check("new sheet resets; Unfold early works after 2 lines", pg.evaluate("folded.done") and pg.evaluate("folded.count") == 2)
    pg.click("#again"); pg.click("#add")
    check("an empty line is refused", pg.evaluate("folded.count") == 0 and "Write a line first" in pg.inner_text("#msg"))
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("phone overflow 0, no JS errors", ov == 0 and not errs, f"overflow={ov} errs={errs}")
    pg.set_viewport_size({"width": 760, "height": 1000})
    for line in MY[:2]: pg.click("#line"); pg.keyboard.type(line); pg.keyboard.press("Enter")
    pg.screenshot(path=str(D.parents[1] / "tools" / "_folded_look.png"), full_page=True)
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
