"""Cycle 129: Penrose (P3) tiling by subdividing Robinson triangles; independent of the page's JavaScript.
Kind 0 = thin-rhombus half, kind 1 = thick-rhombus half. Rules (P3, golden ratio PHI):
  thin  (A,B,C): P = A + (B-A)/PHI            -> thin (C,P,B), thick (P,C,A)
  thick (A,B,C): Q = B + (A-B)/PHI, R = B + (C-B)/PHI -> thick (R,C,A), thick (Q,R,B), thin (R,Q,A)
Prediction: thick/thin -> PHI, within 0.001 by generation 8. Also: subdivision keeps the total area."""
import cmath, json, math
from pathlib import Path
PHI = (1 + 5 ** 0.5) / 2
def wheel():
    tris = []
    for i in range(10):
        B = cmath.rect(1, (2 * i - 1) * math.pi / 10); C = cmath.rect(1, (2 * i + 1) * math.pi / 10)
        if i % 2 == 0: B, C = C, B
        tris.append((0, 0j, B, C))
    return tris
def subdivide(tris):
    out = []
    for k, A, B, C in tris:
        if k == 0:
            P = A + (B - A) / PHI; out += [(0, C, P, B), (1, P, C, A)]
        else:
            Q = B + (A - B) / PHI; R = B + (C - B) / PHI; out += [(1, R, C, A), (1, Q, R, B), (0, R, Q, A)]
    return out
area = lambda tris: sum(abs(((B - A).conjugate() * (C - A)).imag) / 2 for _, A, B, C in tris)
if __name__ == "__main__":
    tris = wheel(); a0 = area(tris); rows = []
    for g in range(11):
        thin = sum(1 for t in tris if t[0] == 0); thick = len(tris) - thin
        rows.append({"gen": g, "thin": thin, "thick": thick, "area": area(tris)})
        print(f"gen {g:2d}: {thin:7d} thin, {thick:7d} thick" + (f", ratio {thick / thin:.6f}" if thin else ""))
        tris = subdivide(tris)
    r8 = rows[8]["thick"] / rows[8]["thin"]
    area_ok = all(abs(r["area"] - a0) < 1e-9 for r in rows)
    print(f"area kept at every generation: {area_ok}")
    print("PREDICTION", "HELD" if abs(r8 - PHI) < 0.001 else "FAILED", f"(gen 8 ratio {r8:.6f} vs phi {PHI:.6f})")
    (Path(__file__).resolve().parent / "counts.json").write_text(json.dumps(rows), encoding="utf-8")
