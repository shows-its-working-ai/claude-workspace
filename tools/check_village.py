"""Upper Wenning hangs together (cycle 265). The village is whatever the MAP's captions link to: every such piece must
exist and must link back to the map, so a new Upper Wenning piece added to the map can't forget the way back. Reads
the built HTML; the links are resolved as a browser would, relative to each page. Control: the link detector finds
no map link on The Tuner (not set in the village), so 'links back' is a real distinction."""
import re, sys
from pathlib import Path
from urllib.parse import urljoin
ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "art" / "34-wenning" / "index.html"
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def targets(page):   # every href on a page, resolved to a file path (fragments and queries dropped)
    base = page.as_uri(); html = page.read_text(encoding="utf-8")
    hrefs = re.findall(r'href="([^"#?]+)', html) + re.findall(r"\['[^']+', '([^']+)'\]", html)   # plain links, and the map's caption links
    return {Path(urljoin(base, h).replace("file:///", "")).resolve() for h in hrefs if not h.startswith(("http", "mailto"))}
links_map = lambda page: MAP.resolve() in targets(page)
pieces = sorted(targets(MAP) - {MAP.resolve(), (ROOT / "index.html").resolve()})   # everything the map links to, except itself and home
check("the map links to the village's pieces (at least The Marrow, The Jam, The Folding Chairs)",
      {"41-the-marrow.html", "45-the-folding-chairs.html"} <= {p.name for p in pieces} and any("33-jam" in str(p) for p in pieces), [str(p.relative_to(ROOT)) for p in pieces])
for p in pieces:
    check(f"{p.relative_to(ROOT)}: exists and links back to the map", p.exists() and links_map(p))
tuner = links_map(ROOT / "writing" / "02-the-tuner.html")
check("control: The Tuner (not in the village) has no map link", not tuner, "NOT SEEN" if tuner else "SEEN")
print("VILLAGE OK" if ok else "VILLAGE BROKEN"); sys.exit(0 if ok else 1)
