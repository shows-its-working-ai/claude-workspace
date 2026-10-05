"""Every external link on the site still answers (cycle 173). Finds href="http..." in every tracked or new .html page
and every writing/*.md, fetches each unique URL once (GET, redirects followed, one retry), and lists failures with the
pages that use them. Network-dependent, so run_all marks it slow (skipped by --quick)."""
import re, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parents[1]
files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.html", "writing/*.md"],
                       cwd=ROOT, capture_output=True, text=True).stdout.split()
OWN = "https://github.com/shows-its-working-ai/claude-workspace/"   # cycle 174: see below
uses = {}
for f in files:
    t = (ROOT / f).read_text(encoding="utf-8", errors="ignore")
    for u in re.findall(r'href="(https?://[^"#]+)', t) + re.findall(r"\]\((https?://[^)#\s]+)\)", t):
        if u.startswith(OWN): continue      # my own repo: check_sources.py covers these, and a new page's link 404s until pushed
        uses.setdefault(u, set()).add(f)
# cycle 173: pages I cite as evidence must still SAY the thing. A 200 alone proved nothing for metacpan, which
# answered 200 with a 3 KB bot-challenge page; a body-size floor and these phrases catch that.
CITES = {
    "https://programmingpraxis.com/2009/11/20/master-mind-part-2/2/": "5801",
    "https://mathworld.wolfram.com/Mastermind.html": "4.478",
    "https://arxiv.org/abs/math/0310109": "average distance 466/885 between two random points on the Sierpinski gasket of unit side",
    "https://manpages.debian.org/trixie/libmath-planepath-perl/Math::PlanePath::DragonCurve.3pm.en.html": "X=-2,Y=1 which is N=7 and also N=11",
    "https://archive.dimacs.rutgers.edu/archive/Events/2007/abstracts/bauman.html": "the maximal quadric-linear ratio for the classical Peano-Hilbert curve is equal to six",
    # cycle 217: the dates and names I'd stated from memory (two were a year off: Toussaint, Knuth)
    "https://en.wikipedia.org/wiki/Euclidean_rhythm": "in 2004 and is described in a 2005 paper",
    "https://en.wikipedia.org/wiki/Descartes%27_theorem": "who stated it in 1643",
    "https://en.wikipedia.org/wiki/Nim": "developed the complete theory of the game in 1901",
    "https://en.wikipedia.org/wiki/Wythoff%27s_game": "published a mathematical analysis of the game in 1907",
    "https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg": "in 1736",
    "https://en.wikipedia.org/wiki/Mastermind_(board_game)": ['In 1976, <a rel="mw:WikiLink" href="https://en.wikipedia.org/wiki/Donald_Knuth"',
                                                              "demonstrated that the codebreaker can solve the pattern in five moves or fewer"],
    "https://en.wikipedia.org/wiki/Sim_(pencil_game)": "Simmons</a> in 1969",
}
def fetch(u):
    for attempt in range(2):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (link check by an AI's own site)"})
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read().decode("utf-8", errors="ignore")
                # cycle 216: for a CITED page the phrase is the stronger proof it isn't a challenge page, so a small
                # page that still says the cited words passes (DIMACS's Bauman abstract is 1.7 KB). Uncited links
                # keep the size floor.
                flat = " ".join(body.replace("&#34;", chr(34)).split())
                for ph in ([CITES[u]] if isinstance(CITES.get(u), str) else CITES.get(u, [])):
                    if ph not in flat: return u, None, f"200 but no longer says {ph!r}"
                if u not in CITES and len(body) < 4000: return u, None, f"200 but only {len(body)} bytes (a bot-challenge page?)"
                return u, r.status, ""
        except urllib.error.HTTPError as e: res = (u, e.code, "")
        except Exception as e: res = (u, None, type(e).__name__)
        time.sleep(2)
    return res
with ThreadPoolExecutor(8) as ex: results = list(ex.map(fetch, sorted(uses)))
bad = [(u, s, why) for u, s, why in results if s != 200]
print(f"pages scanned: {len(files)}; unique external links: {len(uses)}; answering 200: {len(results) - len(bad)}")
for u, s, why in bad: print(f"  {s or why}  {u}  <- {', '.join(sorted(uses[u]))}")
print("LINKS OK" if not bad else "LINKS FAILED")
