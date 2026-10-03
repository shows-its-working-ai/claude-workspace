"""Clicks through EVERY path of the story in Claude's own browser; each must land on the ending the
graph says it should, with that ending's title shown."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
S = json.load(open(D / "story.json", encoding="utf-8")); N = S["nodes"]
def paths(k, acc):
    if "ending" in N[k]: yield acc, k; return
    for label, t in N[k]["choices"]: yield from paths(t, acc + [label])
ok, n = True, 0
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    for labels, want in paths(S["start"], []):
        pg.evaluate(f"show('{S['start']}')")
        for label in labels: pg.get_by_role("button", name=label, exact=True).click()
        got = pg.evaluate("document.body.dataset.node"); shown = N[want]["ending"] in pg.inner_text("#end")
        n += 1; good = got == want and shown; ok &= good
        if not good: print("FAIL path", labels, "->", got, "want", want)
    tally = pg.inner_text("#end")
    print(f"{n} paths clicked through; final tally line: {tally.splitlines()[0]}")
    pg.set_viewport_size({"width": 390, "height": 800})
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    print("phone overflow:", ov, "| js errors:", errs); ok &= ov == 0 and not errs and "3 of 3" in tally
    ctx.close()
print("ALL PASS" if ok else "FAILURES")
