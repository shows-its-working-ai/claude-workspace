"""Cycle 152: Wythoff's game by brute force (bottom-up table over a, b <= N) vs the Beatty-pair formula
(floor(n phi), floor(n phi^2)). Uses exact integer arithmetic for the floors: floor(n*phi) = (n + isqrt(5 n^2)) // 2."""
from math import isqrt
N = 300
lose = [[False] * (N + 1) for _ in range(N + 1)]
for a in range(N + 1):
    for b in range(N + 1):
        win = any(lose[a - k][b] for k in range(1, a + 1)) or any(lose[a][b - k] for k in range(1, b + 1)) \
              or any(lose[a - k][b - k] for k in range(1, min(a, b) + 1))
        lose[a][b] = not win
brute = {(a, b) for a in range(N + 1) for b in range(N + 1) if lose[a][b]}
formula = set()
for n in range(0, N + 1):
    lo = (n + isqrt(5 * n * n)) // 2; hi = lo + n          # floor(n phi^2) = floor(n phi) + n
    if hi <= N: formula |= {(lo, hi), (hi, lo)}
print(f"losing positions with heaps <= {N}: brute force {len(brute)}, formula {len(formula)}")
print("first few:", sorted(p for p in brute if p[0] <= p[1])[:8])
print("PREDICTION", "HELD" if brute == formula else "FAILED", "(losing positions == golden-ratio Beatty pairs)")
