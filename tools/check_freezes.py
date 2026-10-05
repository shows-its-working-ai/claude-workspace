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
tracked = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
pages = args or [f for f in tracked if f.endswith(".html") and "template" not in f]
# cycle 146: in the quick gate (CW_QUICK=1) only pages changed since the last commit are timed (plus the controls);
# the full run times every page. 48 pages x 2 loads, alone, was most of an 11-minute gate.
import os
if not args and os.environ.get("CW_QUICK") == "1":
    changed = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    changed += subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    pages = [f for f in pages if f in changed] + [f for f in changed if f.endswith(".html") and f not in pages and "template" not in f]
    # cycle 268: "git diff --name-only HEAD" lists DELETED files too, so removing a page made this load a file that
    # no longer exists (the first time I'd ever deleted a page). Only time pages that are actually there.
    pages = [f for f in pages if (ROOT / f).exists()]
    print(f"quick mode: timing {len(pages)} changed page(s)")
# cycle 142: Chrome's 'longtask' entries never arrived in the throwaway test profile, so under run_all this check
# measured nothing (a mutant with a 3.9 s freeze survived). Measure directly instead, the same in any profile:
#  - script blocking during load = time from document start to DOMContentLoaded (local files: parsing is ~instant);
#  - after that, a 10 ms heartbeat; the longest gap between beats is the longest freeze.
INIT = """(() => { const t0 = performance.now(); window.__long = [];
  document.addEventListener('DOMContentLoaded', () => {
    window.__long.push(performance.now() - t0);
    let last = performance.now(); setInterval(() => { const t = performance.now(); if (t - last > 50) window.__long.push(t - last); last = t; }, 10);
  }); })();"""
rows = []
# cycle 143: built-in positive controls, measured by the very same code in the very same browser profile, every run.
# (Cycle 141's version passed for a cycle while seeing nothing; a check must prove it can see before it says "OK".)
import tempfile
BUSY = "const e = performance.now() + 400; while (performance.now() < e) {}"
CONTROLS = {"blocks while loading": (f"<script>{BUSY}</script>", 350, None),
            "blocks just after loading": (f"<script>setTimeout(() => {{ {BUSY} }}, 300)</script>", 350, None),
            "calm": ("<p>calm</p>", None, 50)}
tmp = Path(tempfile.mkdtemp())
with sync_playwright() as p:
    ctx = open_browser(p); ctx.add_init_script(INIT); pg = ctx.new_page(); pg.set_viewport_size({"width": 390, "height": 800})
    controls_ok = True
    for name, (body, at_least, at_most) in CONTROLS.items():
        f = tmp / (name.replace(" ", "_") + ".html"); f.write_text(f"<!doctype html><body>{body}</body>", encoding="utf-8")
        pg.goto(f.as_uri()); pg.wait_for_timeout(1500)
        w = max(pg.evaluate("window.__long") or [0])
        good = (at_least is None or w >= at_least) and (at_most is None or w <= at_most)
        controls_ok &= good; print(f"control '{name}': {w:.0f} ms {'ok' if good else 'WRONG'}")
    print("CONTROLS OK" if controls_ok else "CONTROLS FAILED (this checker cannot see freezes here)")
    for f in pages:
        # cycle 143: load twice and keep the smaller worst-case: a real freeze happens on every load, a cold-start spike
        # doesn't (All 88 read 370 ms once in the gate and 183 ms otherwise). The controls are measured once and must
        # still be seen, so this can't hide a real one.
        reads = []
        for _ in range(2):
            pg.goto((ROOT / f).as_uri()); pg.wait_for_timeout(1500)
            L = pg.evaluate("window.__long"); reads.append((max(L) if L else 0.0, len(L or [])))
        w, n = min(reads); rows.append((w, f, n))
    ctx.close()
rows.sort(reverse=True)
for worst, f, n in rows[:12]: print(f"{worst:8.0f} ms  ({n:2d} long tasks)  {f}")
print(f"{len(rows)} pages; {sum(1 for r in rows if r[0] > 500)} block > 500 ms; worst {rows[0][0]:.0f} ms ({rows[0][1]})" if rows else "0 pages to time")
if limit is not None:
    bad = [f for w, f, _ in rows if w > limit]
    print("FREEZES OK" if not bad and controls_ok else f"FREEZES OVER {limit:.0f} ms (or controls failed): {bad}")
