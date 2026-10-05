"""Upper Wenning: the map must agree with the stories. Read from the SVG here in Python (not from the page's JS):
the post office is LOWER than the hall (The Jam: Hen walks "back up the hill" from it), and Hill Lane at the scale bar
is a walk that brackets the story's 15 minutes (1:30 to 1:45) at 4 to 5 km/h; the page's own km/minutes readout says
the same. The captions' story details really are in the stories. REAL clicks and keyboard show each place; every link
in a caption points at a file that exists; phone width; no JS errors. Control: the elevation reader gives 120 m at
the hilltop and the 40 m floor at a map corner, so 'lower' is a reading it can actually make."""
import math, re, sys
from pathlib import Path
from urllib.parse import unquote, urlparse
D = Path(__file__).resolve().parent; ROOT = D.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mybrowser import open_browser
from playwright.sync_api import sync_playwright
html = (D / "index.html").read_text(encoding="utf-8")
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
rings = [(int(e), float(cx), float(cy), float(rx), float(ry)) for e, cx, cy, rx, ry in
         re.findall(r'data-elev="(\d+)" cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)"', html)]
def elev(x, y): return max([e for e, cx, cy, rx, ry in rings if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1] + [40])
at = {k: tuple(map(float, v.split(","))) for k, v in re.findall(r'data-place="(\w+)" data-elev-at="([\d.,]+)"', html)}
seen = len(rings) == 4 and elev(600, 140) == 120 and elev(5, 5) == 40
check("control: 120 m at the hilltop, the 40 m floor at a map corner", seen, "SEEN" if seen else "NOT SEEN")
check("the post office is lower than the hall ('back up the hill')", elev(*at["post"]) < elev(*at["hall"]), f"{elev(*at['post'])} m vs {elev(*at['hall'])} m")
pts = [tuple(map(float, p.split(","))) for p in re.search(r'id="lane" points="([^"]+)"', html)[1].split()]
check("Hill Lane runs from the post office to the hall", math.dist(pts[0], at["post"]) < 15 and math.dist(pts[-1], at["hall"]) < 30)
km = sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) * 2 / 1000   # scale bar: 100 units = 200 m
fast, slow = km / 5 * 60, km / 4 * 60
check("the lane is a 15-minute walk at 4-5 km/h (1:30 -> 1:45)", fast <= 15 <= slow, f"{km:.2f} km, {fast:.1f} to {slow:.1f} min")
check("the scale bar really is 100 units for 200 m", 'd="M0 0 h100' in html and ">200 m<" in html)
marrow = (ROOT / "writing" / "41-the-marrow.md").read_text(encoding="utf-8"); jam = (ROOT / "projects" / "33-jam" / "story.json").read_text(encoding="utf-8")
for phrase, src, name in [("Twelve kilos", marrow, "The Marrow"), ("bread", marrow, "The Marrow"), ("one window and one lock", jam, "The Jam"),
                          ("half past one", jam, "The Jam"), ("ran the post office", marrow, "The Marrow")]:
    check(f"caption detail is in {name}: '{phrase}'", phrase in src)
with sync_playwright() as p:
    ctx = open_browser(p); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((D / "index.html").as_uri()); pg.wait_for_function("window.wenning !== undefined")
    note = pg.inner_text(".note")
    check("the page's readout matches", f"{km:.1f} km" in note and f"{round(fast)} to {round(slow)} minutes" in note, note[note.find('it'):][:60])
    for key, title in [("hall", "The village hall"), ("post", "The post office"), ("church", "St Wenna's"), ("shelter", "The bus shelter")]:
        pg.click(f'.place[data-place="{key}"]')
        check(f"a real click on '{key}' shows its caption", pg.evaluate("wenning.shown") == key and pg.inner_text("#cap h2") == title)
        for href in pg.eval_on_selector_all("#cap a", "as => as.map(a => a.href)"):
            check(f"   its link exists: {href.split('claude-workspace/')[-1]}", Path(unquote(urlparse(href).path.lstrip("/"))).exists())
    pg.focus('.place[data-place="church"]'); pg.keyboard.press("Enter")
    check("keyboard: Enter on the church shows it", pg.evaluate("wenning.shown") == "church" and "St Wenna" in pg.inner_text("#cap h2"))
    pg.set_viewport_size({"width": 390, "height": 800})
    check("phone width: no sideways scroll", pg.evaluate("document.documentElement.scrollWidth - innerWidth") == 0)
    check("no JS errors", not errs, errs)
    ctx.close()
print("ALL PASS" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)
