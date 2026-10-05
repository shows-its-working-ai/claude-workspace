"""Kissing Circles: the (-1, 2, 2, 3) Apollonian gasket, generated and checked EXACTLY.
A circle is (k, kx, ky): curvature and curvature*centre, all integers. Swapping circle d out of a Descartes
quadruple (a, b, c, d) gives the other circle in the same gap: k' = 2(ka+kb+kc) - kd, and the same for kx, ky.
Predictions (journal, cycle 210): (a) every curvature is an integer; (b) every new circle is exactly tangent to its
three parents; (c) no two circles overlap; (d) GUESS ~120 circles of curvature <= 100. Control: the wrong rule
k' = ka+kb+kc+kd must be SEEN to give non-tangent circles."""
import json, sys
from fractions import Fraction as F
from pathlib import Path
D = Path(__file__).resolve().parent

def swap(q, i, rule):
    o = [q[j] for j in range(4) if j != i]
    return tuple(rule(sum(c[t] for c in o), q[i][t]) for t in range(3))

def tangent(c1, c2):                  # |z1 - z2| == |1/k1 + 1/k2|, exactly
    (k1, x1, y1), (k2, x2, y2) = c1, c2
    dx, dy = F(x1, k1) - F(x2, k2), F(y1, k1) - F(y2, k2)
    return dx * dx + dy * dy == (F(1, k1) + F(1, k2)) ** 2

def gasket(K, rule=lambda s, d: 2 * s - d):
    outer, a, b = (-1, 0, 0), (2, 1, 0), (2, -1, 0)
    top, bot = (3, 0, 2), (3, 0, -2)
    circles = [outer, a, b, top, bot]; bad = 0
    stack = [((outer, a, b, top), 3), ((outer, a, b, bot), 3)]
    while stack:
        q, last = stack.pop()
        for i in range(4):
            if i == last: continue
            new = swap(q, i, rule)
            if new[0] > K or new[0] <= 0: continue
            if not all(tangent(new, q[j]) for j in range(4) if j != i): bad += 1
            if len(circles) > 20000: return circles, bad
            circles.append(new); nq = list(q); nq[i] = new; stack.append((tuple(nq), i))
    return circles, bad

K = int(sys.argv[1]) if len(sys.argv) > 1 else 100
cs, bad = gasket(K)
print(f"circles with curvature <= {K}: {len(cs)} (including the outer one)")
print(f"(a) every curvature is a whole number (automatic from the integer rule; (b) is what ties it to real circles): {all(isinstance(c[0], int) for c in cs)}")
print(f"(b) new circles exactly tangent to their three parents: {bad == 0} ({len(cs) - 5} made)")
pos = [c for c in cs if c[0] > 0]
def apart(c1, c2):
    (k1, x1, y1), (k2, x2, y2) = c1, c2
    dx, dy = F(x1, k1) - F(x2, k2), F(y1, k1) - F(y2, k2)
    return dx * dx + dy * dy >= (F(1, k1) + F(1, k2)) ** 2
inside = all(F(c[1], c[0]) ** 2 + F(c[2], c[0]) ** 2 <= (1 - F(1, c[0])) ** 2 for c in pos)
over = sum(not apart(pos[i], pos[j]) for i in range(len(pos)) for j in range(i))
print(f"(c) no two circles overlap, all inside the outer one: {over == 0 and inside} (pairs checked: {len(pos) * (len(pos) - 1) // 2})")
print(f"(d) GUESS ~120 at curvature <= 100: actual {len(gasket(100)[0])}")
dup = len(cs) - len({c for c in cs})
print(f"no circle made twice: {dup == 0}")
_, badc = gasket(100, rule=lambda s, d: s + d)
print(f"control: wrong rule k' = ka+kb+kc+kd gives {badc} non-tangent circles {'SEEN' if badc else 'NOT SEEN'}")
print("PREDICTION HELD" if all(isinstance(c[0], int) for c in cs) and bad == 0 and over == 0 and inside else "PREDICTION FAILED")
if K == 100:
    json.dump({"curvatures_le_100": sorted(c[0] for c in cs), "count_le_100": len(cs)}, open(D / "apollo.json", "w"), separators=(",", ":"))
