"""Cycle 130: how many kinds of vertex (ring of diamonds around a point) appear in the P3 tiling?
Pairs Robinson triangles into diamonds along their shared base, then for every vertex well inside the patch lists
the diamonds around it as (shape, angle) in angular order, and canonicalises that ring up to rotation and mirror.
Checks: angles around every interior vertex sum to 360; every diamond is two triangles of one kind.
Cycle 131: the literature (de Bruijn) gives EIGHT vertex types for the rhombus tiling, counted with the
matching-rule arrows on the edges. This classifies by shape and angle only and finds 7, so (presumably) one
geometric ring covers two arrow-decorated types. Not resolved here which one."""
import cmath, math
from collections import Counter
from penrose import wheel, subdivide

def key(z): return (round(z.real, 6), round(z.imag, 6))
def diamonds(tris):
    by_base = {}
    for k, A, B, C in tris:
        by_base.setdefault(frozenset((key(B), key(C))), []).append((k, A, B, C))
    out = []
    for pair in by_base.values():
        if len(pair) != 2: continue                                        # rim triangle without a partner
        (k1, A1, B, C), (k2, A2, _, _) = pair
        assert k1 == k2, "a diamond made of two different kinds"
        out.append((k1, [A1, B, A2, C]))
    return out
def ring_types(tris, inner=0.6):
    ds = diamonds(tris); at = {}
    for k, pts in ds:
        for i, v in enumerate(pts):
            a, b = pts[i - 1] - v, pts[(i + 1) % 4] - v
            ang = round(math.degrees(abs(cmath.phase(b / a))))
            mid = cmath.phase((a / abs(a) + b / abs(b)))                    # direction of the corner's middle
            at.setdefault(key(v), []).append((mid, "thick" if k else "thin", ang))
    types = Counter(); bad = 0
    for v, corners in at.items():
        if math.hypot(*v) > inner: continue
        if sum(c[2] for c in corners) != 360: bad += 1; continue
        seq = [(s, a) for _, s, a in sorted(corners)]
        n = len(seq); cands = []
        for r in (seq, seq[::-1]):
            cands += [tuple(r[i:] + r[:i]) for i in range(n)]
        types[min(cands)] += 1
    return types, bad

if __name__ == "__main__":
    t = wheel()
    for _ in range(9): t = subdivide(t)
    types, bad = ring_types(t)
    total = sum(types.values())
    print(f"interior vertices: {total}; angle sums not 360: {bad}")
    for ty, c in types.most_common():
        print(f"  {c:6d}  {c / total:6.2%}  " + " ".join(f"{s[:5]}{a}" for s, a in ty))
    print(f"distinct vertex kinds: {len(types)}")
    print("PREDICTION", "HELD" if len(types) == 7 else "FAILED", "(exactly 7 kinds)")
