"""Poems keep their lines (cycle 262: every poem had been rendering as run-together prose since cycle 3).
Verse paragraphs appear on EXACTLY the poem pages listed here, and nowhere else (the 62-character rule in build_site
is a heuristic; this pins what it decided). In a real browser, every verse paragraph shows as many lines as its
source has, and a prose page (The Tuner, wrapped at about 78) shows each paragraph as one run of text.
Control: on a poem page, removing the verse class in the page makes the same stanza collapse to one line, so the
line count really depends on the fix."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
POEMS = {"03-three-small-poems", "09-three-corrections", "17-four-small-poems", "25-folds", "29-four-results",
         "38-three-small-poems", "42-ordinary-things", "46-the-night-porter"}
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
has = {f.stem for f in (ROOT / "writing").glob("*.html") if 'class="verse"' in f.read_text(encoding="utf-8")}
check("verse appears on exactly the poem pages", has == POEMS, f"extra {sorted(has - POEMS)}, missing {sorted(POEMS - has)}")
LINES = "() => [...document.querySelectorAll('p.verse')].map(p => p.innerText.split('\\n').filter(l => l.trim()).length)"
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    for stem in sorted(POEMS):
        src = (ROOT / "writing" / f"{stem}.md").read_text(encoding="utf-8")
        want = [len(b.strip().splitlines()) for b in re.split(r"\n\s*\n", src)
                if len(b.strip().splitlines()) >= 2 and all(len(l) <= 62 for l in b.strip().splitlines()) and not b.lstrip().startswith(("#", "|", "-"))]
        pg.goto((ROOT / "writing" / f"{stem}.html").as_uri()); got = pg.evaluate(LINES)
        check(f"{stem}: every stanza shows its own lines", got == want and len(got) > 0, f"{got} vs {want}")
    pg.goto((ROOT / "writing" / "02-the-tuner.html").as_uri())
    one = pg.evaluate("() => [...document.querySelectorAll('main p')].slice(2, 6).map(p => p.innerText.split('\\n').length)")
    check("a prose page (The Tuner) keeps each paragraph as one run of text", one and all(n == 1 for n in one), one)
    pg.goto((ROOT / "writing" / "46-the-night-porter.html").as_uri())
    before = pg.evaluate("() => document.querySelector('p.verse').innerText.split('\\n').length")
    after = pg.evaluate("() => { const p = document.querySelector('p.verse'); p.className = ''; return p.innerText.split('\\n').length; }")
    check("control: without the fix, the sestina's first stanza collapses to one line", before == 6 and after == 1, f"{before} -> {after}  {'SEEN' if after == 1 else 'NOT SEEN'}")
    check("no JS errors", not errs, errs)
    ctx.close()
print("VERSE OK" if ok else "VERSE FAILED"); sys.exit(0 if ok else 1)
