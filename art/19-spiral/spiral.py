"""Ulam spiral facts (cycle 184). pos(k) = grid position of the k-th number (k = 0 at the centre), the usual
square spiral: right 1, up 1, left 2, down 2, right 3, up 3, ..."""
import json
from pathlib import Path
def positions(N):
    out, x, y, d, step, i = [(0, 0)], 0, 0, 0, 1, 0
    D = [(1, 0), (0, -1), (-1, 0), (0, 1)]                  # right, up, left, down (y grows downward)
    while len(out) < N:
        for _ in range(2):
            for _ in range(step):
                x += D[d][0]; y += D[d][1]; out.append((x, y))
                if len(out) == N: return out
            d = (d + 1) % 4
        step += 1
    return out
def isprime(m):
    if m < 2: return False
    f = 2
    while f * f <= m:
        if m % f == 0: return False
        f += 1
    return True
vals = [n * n + n + 41 for n in range(41)]
p1 = all(isprime(v) for v in vals[:40]) and not isprime(vals[40]) and vals[40] == 41 * 41
P = positions(2000)
pts = [P[v - 41] for v in vals[:40]]                         # spiral starting at 41: number v sits at P[v - 41]
dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
line = all((x - pts[0][0]) * dy == (y - pts[0][1]) * dx for x, y in pts)
diag = abs(dx) == abs(dy) and dx != 0
print(f"(1) 40 primes then 41^2 = {vals[40]}: {p1}")
print(f"(2) positions on one line: {line}; that line is a diagonal: {diag}; first points {pts[:4]}")
prime_count = sum(isprime(v) for v in range(1, 40001))
(Path(__file__).resolve().parent / "spiral.json").write_text(json.dumps({"euler": vals[:40], "primes_to_40000": prime_count}), encoding="utf-8")
print(f"primes up to 40,000: {prime_count}")
print("PREDICTION HELD" if p1 and line and diag else "PREDICTION FAILED")
