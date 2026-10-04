"""Main-thread freezes while each page loads (cycle 141). Records 'longtask' entries (> 50 ms blocks) from the very
start of the page, waits, and reports the longest per page. Usage: check_freezes.py [--limit MS] [pages...]"""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]; limit = None
if "--limit" in args: i = args.index("--limit"); limit = float(args[i + 1]); del args[i:i + 2]
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
pages = args or [f for f in tracked if f.endswith(".html") and "template" not in f]
INIT = """window.__long = []; try { new PerformanceObserver(l => { for (const e of l.getEntries()) window.__long.push(e.duration); })
  .observe({type: 'longtask', buffered: true}); } catch (e) { window.__long = null; }"""
rows = []
with sync_playwright() as p:
    ctx = open_browser(p); ctx.add_init_script(INIT); pg = ctx.new_page(); pg.set_viewport_size({"width": 390, "height": 800})
    for f in pages:
        pg.goto((ROOT / f).as_uri()); pg.wait_for_timeout(1500)
        L = pg.evaluate("window.__long")
        rows.append((max(L) if L else 0.0, f, len(L or [])))
    ctx.close()
rows.sort(reverse=True)
for worst, f, n in rows[:12]: print(f"{worst:8.0f} ms  ({n:2d} long tasks)  {f}")
print(f"{len(rows)} pages; {sum(1 for r in rows if r[0] > 500)} block > 500 ms; worst {rows[0][0]:.0f} ms ({rows[0][1]})")
if limit is not None:
    bad = [f for w, f, _ in rows if w > limit]
    print("FREEZES OK" if not bad else f"FREEZES OVER {limit:.0f} ms: {bad}")
