"""How Long Is a Coastline? (cycle 252). A Koch island whose bumps randomly point out or in (seeded), its self-crossing
check, and a divider walk: from the start, step to the FIRST point further along the coast that is exactly one ruler
away, until you can't. Fits log(length) against log(ruler); the slope is 1 - D. Writes coast.json for the page test."""
import json, math, random, sys
from pathlib import Path
D = Path(__file__).resolve().parent
SEED, DEPTH = 7, 5

def level(pts, signs):
    h = math.sqrt(3) / 2; out = []
    for ((ax, ay), (bx, by)), sg in zip(zip(pts, pts[1:]), signs):
        dx, dy = (bx - ax) / 3, (by - ay) / 3
        p1 = (ax + dx, ay + dy); p3 = (ax + 2 * dx, ay + 2 * dy)
        out += [(ax, ay), p1, (p1[0] + dx / 2 - sg * dy * h, p1[1] + dy / 2 + sg * dx * h), p3]
    return out + [pts[-1]]

def island(seed=SEED, depth=DEPTH, log=None):
    """Each bump points out or in at random. If that makes the coast cross itself, the bumps involved are re-rolled
    and the level rebuilt, until nothing crosses. Every piece keeps the Koch shape (four thirds of its length)."""
    rnd = random.Random(seed); h = math.sqrt(3) / 2
    pts = [(0.0, 0.0), (0.5, h), (1.0, 0.0), (0.0, 0.0)]
    OUT = 1   # the sign that puts a bump outside this triangle (cycle 252: I first guessed -1 and the repair looped forever; the control below now checks it)
    for lv in range(depth):
        signs = [1 if rnd.random() < 0.5 else -1 for _ in range(len(pts) - 1)]; forced = 0
        for tries in range(500):
            new = level(pts, signs); x = crosses(new, lv + 1, every=True)
            if not x: break
            for i, j in x:   # re-roll the bumps involved; the next try rebuilds the level
                for parent in {i // 4, j // 4}: signs[parent] = 1 if rnd.random() < 0.5 else -1; forced += 1
        else: raise RuntimeError(f"level {lv + 1}: still crossing after 500 re-rolls")
        if log is not None: log.append(forced)
        pts = new
    return pts

def crosses(pts, depth=DEPTH, every=False):
    """The first pair of non-adjacent segments that touch (or every pair, with every=True); None/[] if none."""
    def orient(a, b, c): return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    def on(a, b, c): return min(a[0], b[0]) - 1e-12 <= c[0] <= max(a[0], b[0]) + 1e-12 and min(a[1], b[1]) - 1e-12 <= c[1] <= max(a[1], b[1]) + 1e-12
    def hit(p, q, r, s):
        o1, o2, o3, o4 = orient(p, q, r), orient(p, q, s), orient(r, s, p), orient(r, s, q); e = 1e-15
        if ((o1 > e and o2 < -e) or (o1 < -e and o2 > e)) and ((o3 > e and o4 < -e) or (o3 < -e and o4 > e)): return True
        return any(abs(o) <= e and on(a, b, c) for o, a, b, c in [(o1, p, q, r), (o2, p, q, s), (o3, r, s, p), (o4, r, s, q)])
    n = len(pts) - 1; seg = [(pts[i], pts[i + 1]) for i in range(n)]; cell = 1 / 3 ** depth * 2; grid = {}; pairs = set()
    for i, (a, b) in enumerate(seg):
        for gx in range(int(min(a[0], b[0]) // cell), int(max(a[0], b[0]) // cell) + 1):
            for gy in range(int(min(a[1], b[1]) // cell), int(max(a[1], b[1]) // cell) + 1):
                grid.setdefault((gx, gy), []).append(i)
    for ids in grid.values():
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                i, j = ids[x], ids[y]
                if abs(i - j) <= 1 or {i, j} == {0, n - 1}: continue
                if hit(*seg[i], *seg[j]):
                    if not every: return (i, j)
                    pairs.add((min(i, j), max(i, j)))
    return sorted(pairs) if every else None

def walk(pts, r):
    """Divider walk. Returns (steps, leftover straight-line gap back to the start, the visited points)."""
    cur, i, steps, seen = pts[0], 0, 0, [pts[0]]
    while True:
        found = None
        for k in range(i, len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            dx, dy = b[0] - a[0], b[1] - a[1]; fx, fy = a[0] - cur[0], a[1] - cur[1]   # |a + t(b-a) - cur| = r, smallest t >= start
            A = dx * dx + dy * dy; B = 2 * (fx * dx + fy * dy); C = fx * fx + fy * fy - r * r
            disc = B * B - 4 * A * C
            if disc < 0: continue
            ts = sorted(t for t in [(-B - math.sqrt(max(disc, 0))) / (2 * A), (-B + math.sqrt(max(disc, 0))) / (2 * A)] if -1e-9 <= t <= 1 + 1e-9)   # a ruler of 1/3^k lands exactly on vertices: rounding must not lose them
            t0 = 0.0 if k > i else ((cur[0] - a[0]) * dx + (cur[1] - a[1]) * dy) / A
            ts = [min(max(t, 0.0), 1.0) for t in ts if t > t0 + 1e-9]
            if ts: found = (k, (a[0] + ts[0] * dx, a[1] + ts[0] * dy)); break
        if not found: return steps, math.dist(cur, pts[-1]), seen
        i, cur = found; steps += 1; seen.append(cur)

if __name__ == "__main__":
    forced = []; pts = island(log=forced); x = crosses(pts)
    print(f"island: {len(pts) - 1} segments; bump re-rolls per level: {forced}; crosses itself: {x}")
    area = lambda P: sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(P, P[1:])) / 2
    outward = abs(area(level(island(depth=0), [1] * 3))) > abs(area(island(depth=0)))
    print(f"control: OUT really is outward (the sign gives a bigger area than the triangle): {outward}")
    rulers = [3 ** -k for k in range(1, 6)] + [3 ** -k * 0.6 for k in range(1, 5)]
    rows = []
    for r in sorted(rulers, reverse=True):
        n, gap, _ = walk(pts, r); L = n * r + gap; rows.append((r, n, L)); print(f"ruler {r:.5f}: {n} steps, length {L:.3f}")
    xs = [math.log(r) for r, _, _ in rows]; ys = [math.log(L) for _, _, L in rows]; mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sum((a - mx) ** 2 for a in xs); Dfit = 1 - slope
    true = math.log(4) / math.log(3)
    print(f"fitted D = {Dfit:.4f}; exact log4/log3 = {true:.4f}; prediction 2 (within 0.03): {'HELD' if abs(Dfit - true) < 0.03 else 'FAILED'}")
    thirds = [(k, L) for k in range(1, DEPTH + 1) for r, n, L in rows if abs(r - 3 ** -k) < 1e-12]
    exact = len(thirds) == DEPTH and all(abs(L - 3 * (4 / 3) ** k) < 1e-6 for k, L in thirds)   # len: all() of nothing is True
    print(f"every ruler of 1/3^k measures exactly 3*(4/3)^k, as the Koch shape says: {exact}")
    print(f"exact length of the depth-{DEPTH} coast: {3 * (4 / 3) ** DEPTH:.4f} (every segment 1/3^{DEPTH} long, 3*4^{DEPTH} of them)")
    # control: the plain triangle (depth 0) is not fractal: every ruler gives about 3 and the fit says D = 1
    tri = island(depth=0); Ls = [walk(tri, r)[0] * r + walk(tri, r)[1] for r in [0.3, 0.1, 0.03]]
    print(f"control: the plain triangle measures {[round(v, 3) for v in Ls]} {'SEEN' if all(abs(v - 3) < 0.31 for v in Ls) else 'NOT SEEN'}")
    seen = all(abs(v - 3) < 0.31 for v in Ls)
    good = not x and outward and abs(Dfit - true) < 0.03 and exact and seen
    # cycle 252: a mutant (no re-rolling) made this rewrite coast.json from a CROSSING island, and the untracked file
    # wasn't restored afterwards. Only a coast that passes every check may be written.
    if good: json.dump({"seed": SEED, "depth": DEPTH, "rows": rows, "D": Dfit, "crosses": bool(x), "pts": pts}, open(D / "coast.json", "w"))
    print("VERDICT: coast checks out" if good else "VERDICT: PROBLEM"); sys.exit(0 if good else 1)
