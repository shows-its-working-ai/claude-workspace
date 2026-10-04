"""Every public page (except the landing page and templates) must carry a 'source' link whose target is a
folder or file that is actually TRACKED in this repo, so the link can't 404 on GitHub.
--live also fetches each unique link from GitHub and requires HTTP 200."""
import re, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent
PREFIX = "https://github.com/shows-its-working-ai/claude-workspace/"
tracked = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
tracked_set = set(tracked)
pages = [f for f in tracked if f.endswith(".html") and f != "index.html" and "template" not in f and not f.endswith("make.html")]
bad, urls = 0, set()
for f in pages:
    m = re.search(r'<a href="([^"]+)"[^>]*>source</a>', (ROOT / f).read_text(encoding="utf-8"))
    if not m: print("BAD no source link:", f); bad += 1; continue
    url = m.group(1); urls.add(url)
    rel = re.sub(r"^" + re.escape(PREFIX) + r"(tree|blob)/main/", "", url)
    ok = url.startswith(PREFIX) and (rel in tracked_set or any(t.startswith(rel + "/") for t in tracked))
    own = f.startswith(rel + "/") or f == rel.replace(".md", ".html")    # points at THIS page's own source
    if not (ok and own): print("BAD source link:", f, "->", url); bad += 1
print(f"{len(pages)} pages, {len(urls)} distinct source links")
if "--live" in sys.argv:
    for u in sorted(urls):
        try: code = urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=20).status
        except Exception as e: code = getattr(e, "code", str(e))
        if code != 200: print("BAD live", code, u); bad += 1
    print("live: checked", len(urls))
print("SOURCES OK" if bad == 0 else f"{bad} BAD")
