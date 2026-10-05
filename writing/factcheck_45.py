"""Fact-check for writing/45-the-folding-chairs.md, against the village as the map and The Jam already have it:
the walk down Hill Lane "took a quarter of an hour" (the map's lane, at its scale bar, is 15 minutes at 4-5 km/h);
the bus shelter is "at the bottom of Hill Lane, by the post office" (on the map it's near the lane's foot and the post
office, and lower than the hall); Lorna is nineteen here and in The Jam; the vicar's hatchback and folding chairs are
in The Jam too; and the count holds: sixty chairs, fifty-nine after each show. Control: the same walking-time test
on a lane twice as long fails, so it's a real constraint."""
import math, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "45-the-folding-chairs.md").read_text(encoding="utf-8").split())
m = (ROOT / "art" / "34-wenning" / "index.html").read_text(encoding="utf-8")
jam = (ROOT / "projects" / "33-jam" / "story.json").read_text(encoding="utf-8")
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
pts = [tuple(map(float, p.split(","))) for p in re.search(r'id="lane" points="([^"]+)"', m)[1].split()]
walk = lambda P: sum(math.dist(a, b) for a, b in zip(P, P[1:])) * 2 / 1000   # km: the scale bar is 100 units = 200 m
fits = lambda km: km / 5 * 60 <= 15 <= km / 4 * 60
check("'took a quarter of an hour' fits the map's Hill Lane at 4-5 km/h", "It took a quarter of an hour" in s and fits(walk(pts)), f"{walk(pts):.2f} km")
check("control: a lane twice as long would NOT fit", not fits(2 * walk(pts)), "SEEN")
at = {k: tuple(map(float, v.split(","))) for k, v in re.findall(r'data-place="(\w+)" data-elev-at="([\d.,]+)"', m)}
check("the shelter is at the bottom of Hill Lane, by the post office (on the map)", "at the bottom of Hill Lane, by the post office" in s
      and math.dist(at["shelter"], pts[0]) < 60 and math.dist(at["shelter"], at["post"]) < 60, f"{math.dist(at['shelter'], pts[0]):.0f} units from the lane's foot")
check("Lorna is nineteen, here and in The Jam", "Lorna was nineteen" in s and "Lorna, who is nineteen" in jam)
check("the vicar's hatchback and folding chairs are in The Jam too", "hatchback" in s and "hatchback" in jam and "folding chairs" in jam)
check("the count: sixty chairs, fifty-nine after each show, sixty again by Christmas",
      "owns sixty folding chairs" in s and "Every year there are fifty-nine" in s and "the count was back to sixty" in s)
check("the map's church caption links to this story", "45-the-folding-chairs.html" in m)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED"); raise SystemExit(0 if ok else 1)
