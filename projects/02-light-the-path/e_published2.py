"""Cycle 64, step 2: the control failed (a lone E never contains a published E string), so check my READING of the
notation directly: put each published E string into the ether (paper's ether "11111000100110" left and right),
evolve on a long open row, and measure the defect's exact (period, shift) in the middle, away from the edges.
If the strings are read correctly, each should be an exact glider at speed -4/15."""
from fractions import Fraction as Fr
import numpy as np
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
def step(r):                                                     # open row: edges see 0 outside (garbage stays far away)
    p = np.r_[0, r, 0]; return TABLE[4 * p[:-2] + 2 * p[1:-1] + p[2:]]
ETH = np.array([int(c) for c in "11111000100110"], dtype=np.uint8)
E_STRINGS = """1111100000000100110 1111100010000000110 1111100010011000000 1110000011000100110
1111101000011100110 1111100011100011010 111110001001101001111111000100110
1111101100000100110 1111100011110000110 1111100010011001000 1110110011000100110
1111101111011100110 1111100011100111010 1111100010011010110 1111111111000100110""".split()
PAD, T = 60, 400
def measure(s):
    e = np.array([int(c) for c in s], dtype=np.uint8)
    row = np.r_[np.tile(ETH, PAD), e, np.tile(ETH, PAD)]; n = len(row); cut = 14 * PAD + len(e)
    L = np.tile(ETH, n // 14 + 2)[:n]                            # left ether, extended everywhere
    R = np.tile(ETH, n // 14 + 3)[(14 - cut % 14) % 14:][:n]     # right ether, aligned to where it starts
    hist = []
    for t in range(T + 1):
        lo, hi = t + 5, n - t - 5                                # light cone from the open edges
        d = (row != L) & (row != R); d[:lo] = False; d[hi:] = False
        hist.append(d.copy()); row, L, R = step(row), step(L), step(R)
    last = T
    for p in range(1, 61):
        for sh in range(-30, 31):
            if all(np.array_equal(np.roll(hist[last - (r + 1) * p], sh)[300:n - 300], hist[last - r * p][300:n - 300]) for r in range(3)):
                return p, sh, int(hist[last].sum())
    return None
for s in E_STRINGS:
    m = measure(s)
    print(f"{s:34s} ->", f"period {m[0]}, shift {m[1]:+d} = {Fr(m[1], m[0])}, {m[2]} defect cells" if m else "NOT a clean glider")
