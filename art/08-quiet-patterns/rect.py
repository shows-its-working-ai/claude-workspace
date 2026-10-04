"""Cycle 106: on an m x n rectangle, is every quiet pattern that survives the HALF-TURN also mirror-symmetric?
Same method as chiral.py: solve for quiet patterns constant on symmetry orbits, compare dimensions.
Control: a torus rectangle (edges wrap) with the same solver, which should find half-turn-only patterns."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent

def press_cols(m, n, torus=False):
    cols = []
    for r in range(m):
        for c in range(n):
            v = 0
            for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if torus: rr, cc = rr % m, cc % n
                if 0 <= rr < m and 0 <= cc < n: v |= 1 << (rr * n + cc)
            cols.append(v)
    return cols

def invariant_kernel(m, n, gens, torus=False):
    cols = press_cols(m, n, torus); piv = {}; basis = []; seen = set()
    for r in range(m):
        for c in range(n):
            if (r, c) in seen: continue
            orb, stack = {(r, c)}, [(r, c)]
            while stack:
                p = stack.pop()
                for g in gens:
                    q = g(m, n, *p)
                    if q not in orb: orb.add(q); stack.append(q)
            seen |= orb
            x = v = 0
            for rr, cc in orb: x |= 1 << (rr * n + cc); v ^= cols[rr * n + cc]
            pr = x
            while v:
                h = v.bit_length() - 1
                if h in piv: bv, bp = piv[h]; v ^= bv; pr ^= bp
                else: piv[h] = (v, pr); break
            if not v: basis.append(pr)
    return basis

HALF = lambda m, n, r, c: (m - 1 - r, n - 1 - c)
LR = lambda m, n, r, c: (r, n - 1 - c)
UD = lambda m, n, r, c: (m - 1 - r, c)

def quiet(m, n, x):
    cols = press_cols(m, n); b = 0
    for i in range(m * n):
        if x >> i & 1: b ^= cols[i]
    return b == 0

if __name__ == "__main__":
    found = []; nonzero = 0
    for m in range(1, 41):
        for n in range(m + 1, 41):
            h = invariant_kernel(m, n, [HALF]); a = invariant_kernel(m, n, [LR, UD])
            assert all(quiet(m, n, x) for x in h + a)
            nonzero += bool(h)
            if len(h) > len(a): found.append((m, n, len(h), len(a)))
    print(f"rectangles 1 <= m < n <= 40 with any half-turn-symmetric quiet pattern: {nonzero}")
    print("half-turn-only (chiral) rectangles:", found or "none")
    print("PREDICTION", "HELD" if not found else "FAILED", "(no half-turn-only quiet pattern on any rectangle)")
    tor = [(m, n) for m in range(2, 13) for n in range(m + 1, 13)
           if len(invariant_kernel(m, n, [HALF], True)) > len(invariant_kernel(m, n, [LR, UD], True))]
    print("torus control, half-turn-only rectangles m < n <= 12:", tor)
    print("TORUS CONTROL", "OK" if tor else "FAILED (solver may be blind)")
    (D / "rect.json").write_text(json.dumps({"found": found, "torus": tor}), encoding="utf-8")
