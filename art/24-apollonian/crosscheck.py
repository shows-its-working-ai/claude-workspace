"""Independent completeness check for apollo.py: search EVERY quadruple reachable by any swap (no 'don't swap back'
shortcut), deduplicating quadruples as sets, and compare the circles found up to curvature 100 with apollo.json."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent
start = frozenset([(-1, 0, 0), (2, 1, 0), (2, -1, 0), (3, 0, 2)])
seen, todo, circles = {start}, [start], set(start)
while todo:
    q = list(todo.pop())
    for i in range(4):
        o = q[:i] + q[i + 1:]
        new = tuple(2 * sum(c[t] for c in o) - q[i][t] for t in range(3))
        if new[0] > 100: continue
        nq = frozenset(o + [new])
        if nq not in seen: seen.add(nq); todo.append(nq); circles.add(new)
ks = sorted(c[0] for c in circles)
py = json.loads((D / "apollo.json").read_text(encoding="utf-8"))
print(f"quadruples searched: {len(seen)}; circles: {len(circles)}; smallest curvatures: {ks[:14]}")
print("CROSSCHECK OK" if ks == py["curvatures_le_100"] else "CROSSCHECK FAILED")
