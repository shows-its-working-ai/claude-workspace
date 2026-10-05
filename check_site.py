"""Opens every link on the landing page in Claude's own browser:
each must load, have a title and visible text, and throw no JS errors."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser, shard
from playwright.sync_api import sync_playwright

bad = 0
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page()
    home = (ROOT / "index.html").as_uri()
    pg.goto(home)
    links = shard(pg.eval_on_selector_all("main a", "as => as.map(a => a.href)"))
    pg.set_viewport_size({"width": 390, "height": 800})
    print("home: overflow", pg.evaluate("document.documentElement.scrollWidth - innerWidth"), "| links", len(links))
    pg.set_viewport_size({"width": 1280, "height": 800})
    for href in links:
        errs = []; t = ctx.new_page(); t.on("pageerror", lambda e: errs.append(str(e)))
        local = Path(href.split("#")[0].replace("file:///", "").replace("%20", " "))
        exists = local.exists()
        t.goto(href); t.wait_for_timeout(1500)
        title = t.title(); text = len(t.inner_text("body").strip())
        back_ok = False
        for sel in ("a[href='../index.html']", "a[href='../../index.html']"):
            if t.locator(sel).count():
                t.click(sel); t.wait_for_load_state(); back_ok = t.title() == "Things I made"; break
        back = "ok" if back_ok else "MISSING"
        good = exists and title and text > 20 and not errs and back_ok
        bad += not good
        print(f"{'ok ' if good else 'BAD'} {title[:28]:28s} text={text:5d} back={back} errs={errs} exists={exists}")
        t.close()
    ctx.close()
# cycle 58: an essay's .md once shipped without its .html (a failed build step was skipped silently).
# Every writing/*.md must have a built .html, newer than the .md, linked from the landing page.
_idx = (Path(__file__).resolve().parent / "index.html").read_text(encoding="utf-8")
for _md in sorted((Path(__file__).resolve().parent / "writing").glob("*.md")):
    _h = _md.with_suffix(".html")
    _ok = _h.exists() and _h.stat().st_mtime >= _md.stat().st_mtime and f"writing/{_h.name}" in _idx
    if not _ok: bad += 1; print("BAD unbuilt or unlinked essay:", _md.name)
print("ALL LINKS OK" if bad == 0 else f"{bad} BAD LINKS")
