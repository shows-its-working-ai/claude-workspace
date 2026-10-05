"""Crawls the LIVE GitHub Pages site the way check_site.py crawls the local one, and plays one
nonogram live (needs solver.js + generator.js to be served correctly)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "projects" / "04-nonograms"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
from puzzles import line_solve
BASE = "https://shows-its-working-ai.github.io/claude-workspace/"
# cycle 263: GitHub cancelled or queued the Pages deploys of cycles 258-262, so the live site stayed at cycle 257 while
# this script said LIVE SITE OK five times: it crawled whatever the OLD home page linked to. First make sure the live
# site IS this commit: its index.html must match the one just pushed (line endings aside). Wait up to 10 minutes.
import time, urllib.request
want = (ROOT / "index.html").read_bytes().replace(b"\r\n", b"\n")
for attempt in range(21):
    try:
        with urllib.request.urlopen(f"{BASE}index.html?fresh={time.time():.0f}", timeout=30) as r: live = r.read().replace(b"\r\n", b"\n")
    except Exception as e: live = repr(e).encode()
    if live == want: print(f"live index.html matches this commit (after {attempt * 30} s)"); break
    if attempt < 20: time.sleep(30)
else:
    print(f"LIVE IS STALE: after 10 minutes the live index.html ({len(live)} bytes) still isn't this commit's ({len(want)} bytes)"); sys.exit(1)
bad = 0
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page()
    pg.goto(BASE, timeout=60000)
    links = pg.eval_on_selector_all("main a", "as => as.map(a => a.href)")
    print("live home:", pg.title(), "|", len(links), "links")
    for href in links:
        errs = []; t = ctx.new_page(); t.on("pageerror", lambda e: errs.append(str(e)))
        resp = t.goto(href, timeout=60000); t.wait_for_timeout(1200)
        status = resp.status if resp else None; title = t.title(); text = len(t.inner_text("body").strip())
        back_ok = False
        for sel in ("a[href='../index.html']", "a[href='../../index.html']", "a[href='index.html']"):
            if t.locator(sel).count():
                t.click(sel); t.wait_for_load_state(); back_ok = t.title() in ("Things I made", "Little Pictures"); break
        good = status == 200 and title and text > 20 and not errs and back_ok
        bad += not good
        print(f"{'ok ' if good else 'BAD'} {status} {title[:30]:30s} back={back_ok} errs={errs[:1]}")
        t.close()
    g = ctx.new_page(); errs = []; g.on("pageerror", lambda e: errs.append(str(e)))
    g.goto(BASE + "projects/04-nonograms/index.html", timeout=60000); g.click("#surprise")
    z = g.evaluate("({rows: P[0].rows, cols: P[0].cols})"); sol, _ = line_solve(z["rows"], z["cols"])
    for r, row in enumerate(sol):
        for c, v in enumerate(row):
            if v: g.click(f'.cell[data-r="{r}"][data-c="{c}"]')
    won = g.evaluate("document.body.dataset.won") == "1"
    print("live nonogram (Surprise me) solved by clicks:", won, "| errors:", errs); bad += (not won) or bool(errs)
    ctx.close()
print("LIVE SITE OK" if bad == 0 else f"{bad} PROBLEMS")
