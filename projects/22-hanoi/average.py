"""Exact average distance between two positions (ordered pairs, including a position with itself) in the n-disk
Hanoi graph, n = 1..7 (cycle 187)."""
from fractions import Fraction as F
ns = {}; exec(open(__file__.replace("average.py", "hanoi.py"), encoding="utf-8").read().split("bad = []")[0], ns)
from itertools import product
r = []
for n in range(1, 8):
    states = list(product(range(3), repeat=n)); tot = 0
    for s in states: tot += sum(ns["bfs"](s)[0].values())
    avg = F(tot, len(states) ** 2); r.append(float(avg) / 2 ** n)
    print(f"n={n}: average {float(avg):.4f} moves; / 2^n = {r[-1]:.5f}")
g = [b - a for a, b in zip(r, r[1:])]
q = g[-1] / g[-2]                                    # the gaps shrink by about this factor each step
print(f"last gaps {g[-3]:.5f} {g[-2]:.5f} {g[-1]:.5f}, ratio {q:.3f}; geometric extrapolation of the limit: {r[-1] + g[-1] * q / (1 - q):.5f}")
print(f"466/885 = {466 / 885:.5f}")
