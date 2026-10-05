"""Front page 'Take me somewhere at random' (cycle 246): every piece listed under a section heading is a candidate,
each exactly once (the five-minute picks repeat some links), every candidate is a real file, and REAL clicks with
Math.random pinned to the first, middle and last slots land on exactly those pages. Control: the candidate count
equals the sum of the section counts shown in the headings, so a picker that missed a section would be seen."""
import re, sys
from pathlib import Path
from urllib.parse import unquote, urlparse
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
home = (ROOT / "index.html").as_uri()
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(home)
    cands = pg.evaluate("[...new Set([...document.querySelectorAll('main h2 ~ p > a')].map(a => a.href))]")
    shown = sum(int(n) for n in re.findall(r"<span class=\"muted\">\((\d+)\)</span></h2>", (ROOT / "index.html").read_text(encoding="utf-8")))
    check("candidates == the sum of the section counts (each piece once)", len(cands) == shown, f"{len(cands)} vs {shown}")
    missing = [c for c in cands if not Path(unquote(urlparse(c).path.lstrip("/"))).exists()]
    check("every candidate is a real file", not missing, str(missing[:3]))
    for name, frac in (("first", 0.0), ("middle", 0.5), ("last", 0.999999)):
        pg.goto(home); pg.evaluate(f"Math.random = () => {frac}")
        want = cands[int(frac * len(cands))]
        with pg.expect_navigation(): pg.click("#surprise")
        check(f"a real click with random pinned to the {name} slot lands on that page", pg.url == want, pg.url.split("/")[-2:])
    check("no JS errors", not errs, str(errs))
    ctx.close()
print("SURPRISE OK" if ok else "SURPRISE FAILED")
