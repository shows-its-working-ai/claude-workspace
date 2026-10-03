"""Cycle 104: are rotation-invariant quiet patterns always mirror-invariant too?
For each n, solve directly for quiet patterns that are constant on symmetry orbits (C4 = rotations, D4 = rotations
and reflections), and compare the dimensions. No enumeration, so it reaches n = 100.
Cross-check: for n <= 19, the D4 dimension must match quiet.json (2^dim - 1 == number of fully symmetric patterns),
and for small n the C4 dimension is also checked by brute force over the whole kernel."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D))
from quiet import press_cols, kernel_basis, sym_images

def orbits(n, group):
    rot = lambda r, c: (c, n - 1 - r)
    mir = lambda r, c: (r, n - 1 - c)
    gens = [rot] + ([mir] if group == "D4" else [])
    seen, out = set(), []
    for r in range(n):
        for c in range(n):
            if (r, c) in seen: continue
            orb, stack = {(r, c)}, [(r, c)]
            while stack:
                p = stack.pop()
                for g in gens:
                    q = g(*p)
                    if q not in orb: orb.add(q); stack.append(q)
            seen |= orb; out.append(orb)
    return out

def invariant_kernel(n, group):
    """Basis of quiet patterns constant on each orbit, as full-board bitmasks."""
    cols = press_cols(n); piv = {}; basis = []
    for orb in orbits(n, group):
        x = 0
        for r, c in orb: x |= 1 << (r * n + c)
        v = 0
        for r, c in orb: v ^= cols[r * n + c]          # A applied to the orbit's indicator
        pr = x
        while v:
            h = v.bit_length() - 1
            if h in piv: bv, bp = piv[h]; v ^= bv; pr ^= bp
            else: piv[h] = (v, pr); break
        if not v: basis.append(pr)
    return basis

def toggles(cols, x):
    b = 0; i = 0
    while x:
        if x & 1: b ^= cols[i]
        x >>= 1; i += 1
    return b

if __name__ == "__main__":
    py = json.loads((D / "quiet.json").read_text(encoding="utf-8"))
    rows = []; ok = True
    for n in range(1, 101):
        cols = press_cols(n)
        c4, d4 = invariant_kernel(n, "C4"), invariant_kernel(n, "D4")
        assert all(toggles(cols, x) == 0 for x in c4 + d4), f"n={n}: an 'invariant quiet' pattern is not quiet"
        assert all(all(y == x for y in sym_images(n, x)[:4]) for x in c4), f"n={n}: C4 basis not rotation-invariant"
        assert all(all(y == x for y in sym_images(n, x)) for x in d4), f"n={n}: D4 basis not fully invariant"
        if str(n) in py:                                   # cross-check against cycle 103's enumeration
            ok &= 2 ** len(d4) - 1 == len(py[str(n)]["fully_symmetric"])
        if n <= 14 and str(n) in py:                       # brute-force C4 over the whole kernel
            kb = kernel_basis(n); k = len(kb); cnt = 0
            for m in range(1, 1 << k):
                x = 0
                for j in range(k):
                    if m >> j & 1: x ^= kb[j]
                cnt += all(y == x for y in sym_images(n, x)[:4])
            ok &= cnt == 2 ** len(c4) - 1
        rows.append((n, len(c4), len(d4)))
        if c4 or d4: print(f"n={n:2d}: rotation-invariant dim {len(c4)}, fully symmetric dim {len(d4)}"
                           + ("   <-- CHIRAL" if len(c4) > len(d4) else ""))
    chiral = [n for n, a, b in rows if a > b]
    print("cross-checks", "OK" if ok else "FAILED")
    print("chiral sizes:", chiral or "none")
    print("PREDICTION", "HELD" if chiral else "FAILED", "(some n <= 100 has a chiral quiet pattern)")
    # Positive control: on a TORUS board (edges wrap) the same solver DOES find chiral quiet patterns, so "none" above
    # is a fact about the bounded board, not a solver that can't see chirality. Known: n = 5, 6, 10, 12 (cycle 104).
    plain = press_cols
    def press_cols(n):
        cols = []
        for r in range(n):
            for c in range(n):
                v = 0
                for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): v |= 1 << (((r + dr) % n) * n + (c + dc) % n)
                cols.append(v)
        return cols
    tor = [n for n in range(3, 13) if len(invariant_kernel(n, "C4")) > len(invariant_kernel(n, "D4"))]
    press_cols = plain
    print("torus chiral sizes n <= 12:", tor)
    print("TORUS CONTROL", "OK" if tor == [5, 6, 10, 12] else "FAILED")
    (D / "chiral.json").write_text(json.dumps({"rows": rows, "chiral": chiral}), encoding="utf-8")
