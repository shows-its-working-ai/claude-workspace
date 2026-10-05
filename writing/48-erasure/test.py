"""Early Rising, Erased: an INDEPENDENT erasure check (a regex: the poem's words, in order, each separated by any
run of other text, must match the source; the build uses a greedy scan instead), then in a real browser: the page's
full text, normalised, IS Mrs Beeton's two paragraphs (nothing altered or added); the dark words in it, in order,
are exactly the poem; the poem keeps its lines; a REAL click shows and hides the page; the note's counts are right;
the Gutenberg link is there; phone; no JS errors. Control: the poem with two words swapped fails the regex."""
import json, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
source = (D / "source.txt").read_text(encoding="utf-8"); poem = (D / "poem.txt").read_text(encoding="utf-8")
words = lambda t: [w for w in re.split(r"[^a-z]+", t.lower()) if w]
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def erasure(pw):
    pat = r"\b" + r"\b(?:[^a-z]+[a-z]+)*?[^a-z]+\b".join(map(re.escape, pw)) + r"\b"
    return re.search(pat, " ".join(words(source))) is not None
pw = words(poem)
check("independent check: the poem's words are in the source in order (regex)", erasure(pw), f"{len(pw)} words")
swapped = pw[:]; swapped[1], swapped[2] = swapped[2], swapped[1]
bad = erasure(swapped)
check("control: with two words swapped it is NOT an erasure", not bad, "NOT SEEN" if bad else "SEEN")
E = json.loads((D / "erasure.json").read_text(encoding="utf-8"))
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri())
    check("the page starts hidden", not pg.is_visible("#page"))
    pg.click("#show")
    check("a real click shows the page it came from", pg.is_visible("#page") and pg.get_attribute("#show", "aria-expanded") == "true")
    check("the page's text IS her two paragraphs, nothing altered", words(pg.inner_text("#page")) == words(source))
    dark = words(" ".join(pg.eval_on_selector_all("#page .k", "ks => ks.map(k => k.textContent)")))
    check("the dark words, in order, are exactly the poem", dark == pw, f"{len(dark)} dark words")
    pg.click("#show"); check("clicking again hides it", not pg.is_visible("#page"))
    lines = pg.evaluate("() => [...document.querySelectorAll('#poem .verse')].map(p => p.innerText.split('\\n').filter(l => l.trim()).length)")
    want = [len(s.strip().splitlines()) for s in poem.strip().split("\n\n")]
    check("the poem keeps its lines and stanzas", lines == want, f"{lines} vs {want}")
    note = " ".join(pg.inner_text(".note").split())
    n = len(re.findall(r"\S+", poem))   # 'self-indulgence' is one word as written (my first count split it and got 79)
    check("the note's counts are right", f"{n} words kept out of {E['n_source']}" in note and E["n_poem"] == n, f"{n} kept")
    check("the Gutenberg source is linked", pg.locator('a[href="https://www.gutenberg.org/ebooks/10136"]').count() == 1)
    pg.set_viewport_size({"width": 390, "height": 800}); pg.click("#show")
    check("phone width: no sideways scroll, page open", pg.evaluate("document.documentElement.scrollWidth - innerWidth") == 0)
    check("no JS errors", not errs, errs)
    ctx.close()
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)
