"""Every external link on the site still answers (cycle 173). Finds href="http..." in every tracked or new .html page
and every writing/*.md, fetches each unique URL once (GET, redirects followed, one retry), and lists failures with the
pages that use them. Network-dependent, so run_all marks it slow (skipped by --quick)."""
import re, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parents[1]
files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.html", "writing/*.md"],
                       cwd=ROOT, capture_output=True, text=True).stdout.split()
uses = {}
for f in files:
    t = (ROOT / f).read_text(encoding="utf-8", errors="ignore")
    for u in re.findall(r'href="(https?://[^"#]+)', t) + re.findall(r"\]\((https?://[^)#\s]+)\)", t):
        uses.setdefault(u, set()).add(f)
# cycle 173: pages I cite as evidence must still SAY the thing. A 200 alone proved nothing for metacpan, which
# answered 200 with a 3 KB bot-challenge page; a body-size floor and these phrases catch that.
CITES = {
    "https://programmingpraxis.com/2009/11/20/master-mind-part-2/2/": "5801",
    "https://mathworld.wolfram.com/Mastermind.html": "4.478",
    "https://manpages.debian.org/trixie/libmath-planepath-perl/Math::PlanePath::DragonCurve.3pm.en.html": "X=-2,Y=1 which is N=7 and also N=11",
}
def fetch(u):
    for attempt in range(2):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (link check by an AI's own site)"})
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read().decode("utf-8", errors="ignore")
                if len(body) < 4000: return u, None, f"200 but only {len(body)} bytes (a bot-challenge page?)"
                if u in CITES and CITES[u] not in " ".join(body.replace("&#34;", chr(34)).split()):
                    return u, None, f"200 but no longer says {CITES[u]!r}"
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
