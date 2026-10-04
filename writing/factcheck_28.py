"""Fact-check for writing/28-the-round.md against the made-up town's map (defined here): 7 streets, 6 corners; the
corners' street counts; exactly two odd corners, Church and Bridge; the two routes between them (Mill 300+200=500,
Green 150+200=350) and that the Green is the shortest path; streets total 1,850 yards; the best round 1,850+350 =
2,200; the walked route is a real closed walk from the Church using every street, with exactly the Green stretch
walked twice, and is 2,200 yards long. Numbers must appear in the story as written."""
import heapq
from pathlib import Path
s = " ".join((Path(__file__).resolve().parent / "28-the-round.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
streets = {("Church", "Mill"): 300, ("Mill", "Bridge"): 200, ("Bridge", "Station"): 400, ("Station", "School"): 250,
           ("School", "Church"): 350, ("Church", "Green"): 150, ("Green", "Bridge"): 200}
corners = sorted({c for e in streets for c in e})
deg = {c: sum(c in e for e in streets) for c in corners}
check("seven streets, six corners", len(streets) == 7 and len(corners) == 6 and "Seven streets, six corners" in s)
check("counts: Mill, Station, School, Green two; Church, Bridge three",
      [deg[c] for c in ("Mill", "Station", "School", "Green")] == [2, 2, 2, 2] and deg["Church"] == deg["Bridge"] == 3
      and "The Mill had two. The Station had two. The School had two, and the Green had two. The Church had three, and so did the Bridge." in s)
check("exactly two odd corners: Church and Bridge", sorted(c for c in corners if deg[c] % 2) == ["Bridge", "Church"])
L = lambda a, b: streets.get((a, b)) or streets.get((b, a))
check("by the Mill 300 + 200 = 500", L("Church", "Mill") + L("Mill", "Bridge") == 500 and "three hundred yards to the Mill and two hundred more to the Bridge, five hundred in all" in s)
check("by the Green 150 + 200 = 350", L("Church", "Green") + L("Green", "Bridge") == 350 and "a hundred and fifty to the Green and two hundred to the Bridge, three hundred and fifty" in s)
dist = {c: 1e9 for c in corners}; dist["Church"] = 0; q = [(0, "Church")]
while q:
    d, c = heapq.heappop(q)
    for (a, b), w in streets.items():
        for x, y in ((a, b), (b, a)):
            if x == c and d + w < dist[y]: dist[y] = d + w; heapq.heappush(q, (d + w, y))
check("the long way by the School and Station is 1,000 and mentioned", L("Church", "School") + L("School", "Station") + L("Station", "Bridge") == 1000 and "the long way round by the School and the Station, a thousand yards" in s)
check(f"shortest Church->Bridge is {dist['Bridge']} (the Green way)", dist["Bridge"] == 350)
total = sum(streets.values())
check(f"all streets = {total}", total == 1850 and "one thousand eight hundred and fifty yards" in s)
check("best round = 1,850 + 350 = 2,200", total + dist["Bridge"] == 2200 and "Two thousand two hundred." in s)
walk = ["Church", "Mill", "Bridge", "Station", "School", "Church", "Green", "Bridge", "Green", "Church"]
legs = [tuple(sorted(p)) for p in zip(walk, walk[1:])]
from collections import Counter
cnt = Counter(legs); every = all(cnt[tuple(sorted(e))] >= 1 for e in streets)
twice = sorted(k for k, v in cnt.items() if v == 2)
check("Friday's route: closed, from the Church, every street, only Church-Green and Green-Bridge twice",
      walk[0] == walk[-1] == "Church" and all(L(a, b) for a, b in zip(walk, walk[1:])) and every
      and twice == [("Bridge", "Green"), ("Church", "Green")] and len(cnt) == 7
      and "Church, Mill, Bridge, Station, School, Church, Green, Bridge, and then back over the Green to the Church" in s)
check("Friday's route is 2,200 yards", sum(L(a, b) for a, b in zip(walk, walk[1:])) == 2200 and "It came to two thousand two hundred yards" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
