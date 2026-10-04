"""Cycle 155: Grundy values of Wythoff's game, g(a, b) = mex of g over all moves (from one heap, or equally from both).
Checks: symmetry g(a,b) = g(b,a); zeros == the Beatty pairs (exact integers); g(x, 0) = x."""
import json
from math import isqrt
from pathlib import Path
N = 64
g = [[0] * N for _ in range(N)]
for a in range(N):
    for b in range(N):
        seen = {g[a - k][b] for k in range(1, a + 1)} | {g[a][b - k] for k in range(1, b + 1)} | {g[a - k][b - k] for k in range(1, min(a, b) + 1)}
        m = 0
        while m in seen: m += 1
        g[a][b] = m
sym = all(g[a][b] == g[b][a] for a in range(N) for b in range(N))
zeros = {(a, b) for a in range(N) for b in range(N) if g[a][b] == 0}
beatty = set()
for n in range(N):
    lo = (n + isqrt(5 * n * n)) // 2; hi = lo + n
    if hi < N: beatty |= {(lo, hi), (hi, lo)}
row0 = all(g[x][0] == x for x in range(N))
print(f"symmetric: {sym}; zeros == golden pairs: {zeros == beatty} ({len(zeros)}); g(x,0) = x: {row0}; max value {max(map(max, g))}")
print("PREDICTION", "HELD" if sym and zeros == beatty and row0 else "FAILED")
(Path(__file__).resolve().parent / "grundy64.json").write_text(json.dumps(g), encoding="utf-8")
