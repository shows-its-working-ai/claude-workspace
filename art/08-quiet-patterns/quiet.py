"""Quiet patterns (cycle 103): sets of presses on an n x n Lights Out board that change NOTHING (the kernel of the
press matrix over GF(2)). For the deficient sizes found in cycle 101 there are 2^nullity of them (counting "press
nothing").
Prediction (written first, about mathematics): for every deficient n <= 19, at least one non-empty quiet pattern is
symmetric under ALL 8 symmetries of the square (rotations and reflections).
Writes quiet.json: for each deficient n, every quiet pattern's count, the fully symmetric ones, and a basis."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent

def press_cols(n):
    cols = []
    for r in range(n):
        for c in range(n):
            v = 0
            for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n: v |= 1 << (rr * n + cc)
            cols.append(v)
    return cols
def kernel_basis(n):
    cols = press_cols(n); piv = {}; kern = []
    for i, v in enumerate(cols):
        pr = 1 << i
        while v:
            h = v.bit_length() - 1
            if h in piv: bv, bp = piv[h]; v ^= bv; pr ^= bp
            else: piv[h] = (v, pr); break
        if not v: kern.append(pr)
    return kern
def toggles(n, presses):
    cols = press_cols(n); b = 0
    for i in range(n * n):
        if presses >> i & 1: b ^= cols[i]
    return b
def sym_images(n, x):
    cells = [(i // n, i % n) for i in range(n * n) if x >> i & 1]
    maps = [lambda r, c: (r, c), lambda r, c: (c, n - 1 - r), lambda r, c: (n - 1 - r, n - 1 - c), lambda r, c: (n - 1 - c, r),
            lambda r, c: (r, n - 1 - c), lambda r, c: (n - 1 - r, c), lambda r, c: (c, r), lambda r, c: (n - 1 - c, n - 1 - r)]
    out = []
    for f in maps:
        y = 0
        for r, c in cells: rr, cc = f(r, c); y |= 1 << (rr * n + cc)
        out.append(y)
    return out

if __name__ == "__main__":
    result = {}; held = True
    for n in (4, 5, 9, 11, 14, 16, 17, 19):
        basis = kernel_basis(n); k = len(basis)
        all_q = []
        for m in range(1, 1 << k):
            x = 0
            for j in range(k):
                if m >> j & 1: x ^= basis[j]
            all_q.append(x)
        assert all(toggles(n, x) == 0 for x in all_q), "a 'quiet' pattern changed something"
        full = [x for x in all_q if all(y == x for y in sym_images(n, x))]
        held &= len(full) > 0
        result[n] = {"nullity": k, "quiet": len(all_q), "fully_symmetric": [str(x) for x in full], "basis": [str(x) for x in basis]}
        print(f"n={n:2d}: nullity {k:2d}, {len(all_q):6d} non-empty quiet patterns, {len(full)} fully symmetric")
    (D / "quiet.json").write_text(json.dumps(result), encoding="utf-8")
    print("PREDICTION", "HELD" if held else "FAILED", "(every deficient n has a fully symmetric quiet pattern)")
