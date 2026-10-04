"""Cycle 159: Bjorklund's algorithm vs the floor (Bresenham) pattern, up to rotation, for 1 <= k <= n <= 16."""
import json
from pathlib import Path
def bjorklund(k, n):
    if k == 0: return [0] * n
    a, b = [[1] for _ in range(k)], [[0] for _ in range(n - k)]
    while len(b) > 1:
        m = min(len(a), len(b))
        a, b = [a[i] + b[i] for i in range(m)], (a[m:] if len(a) > m else b[m:])
    return [x for s in a + b for x in s]
def floor_pattern(k, n): return [1 if (i * k) // n != ((i - 1) * k) // n or i == 0 else 0 for i in range(n)]
def rotations(p): return {tuple(p[i:] + p[:i]) for i in range(len(p))}
s = lambda p: "".join("x" if v else "." for v in p)
if __name__ == "__main__":
    bad = []; out = {}
    for n in range(1, 17):
        for k in range(1, n + 1):
            b, f = bjorklund(k, n), floor_pattern(k, n)
            out[f"{k},{n}"] = s(b)
            if sum(b) != k or len(b) != n or tuple(f) not in rotations(b): bad.append((k, n, s(b), s(f)))
    print(f"E(3,8) = {out['3,8']}   E(5,8) = {out['5,8']}   E(2,5) = {out['2,5']}   E(3,4) = {out['3,4']}")
    named = tuple(map(int, "10010010")) in rotations(bjorklund(3, 8)) and tuple(map(int, "10110110")) in rotations(bjorklund(5, 8))
    print(f"pairs checked: 136; mismatches: {len(bad)} {bad[:3]}; tresillo & cinquillo found: {named}")
    print("PREDICTION", "HELD" if not bad and named else "FAILED")
    (Path(__file__).resolve().parent / "euclid.json").write_text(json.dumps(out), encoding="utf-8")
