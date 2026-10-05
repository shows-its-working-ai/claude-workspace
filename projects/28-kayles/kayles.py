"""Skittles (Kayles): Grundy values of a row of n pins, where a move removes 1 or 2 adjacent pins (possibly
splitting the row). Predictions (journal, cycle 226): (a) eventually periodic, period 12; (b) GUESS last exception at
n = 70; (c) G(n) > 0 for all n >= 1 (the first player always wins one row). Control: take 1-2 from the END only
gives period 3 (0, 1, 2, ...) - SEEN. A brute-force minimax on small boards cross-checks the Grundy theory."""
import json
from functools import lru_cache
from pathlib import Path
D = Path(__file__).resolve().parent
N = 2000

def mex(s):
    m = 0
    while m in s: m += 1
    return m
G = [0] * (N + 1)
for n in range(1, N + 1):
    opts = set()
    for take in (1, 2):
        for left in range(0, n - take + 1):
            opts.add(G[left] ^ G[n - take - left])
    G[n] = mex(opts)
exc = [n for n in range(13, N + 1) if G[n] != G[n - 12]]
print(f"G(0..23) = {G[:24]}")
print(f"(b) AS I FIRST WROTE IT, 'G(n) = G(n-12) from n = 71': fails; last n with G(n) != G(n-12) is {max(exc)} (G(82) vs G(70))")
# cycle 226: the remembered fact is about the LAST IRREGULAR VALUE: G(n) = G(n+12) for every n >= 71. I translated it
# into a test one period off. The standard reading, tested here:
irr = [n for n in range(0, N - 12 + 1) if G[n] != G[n + 12]]
print(f"(a)+(b) standard reading: G(n) = G(n+12) for all 71 <= n <= {N - 12}; last irregular n = {max(irr)}; irregular: {irr}")
print(f"(c) G(n) > 0 for every 1 <= n <= {N}: {all(g > 0 for g in G[1:])}")
# brute force on positions = sorted tuple of row lengths, total <= 12: who wins by plain minimax
@lru_cache(maxsize=None)
def win(pos):
    for i, r in enumerate(pos):
        for take in (1, 2):
            for left in range(0, r - take + 1):
                rest = pos[:i] + pos[i + 1:] + tuple(x for x in (left, r - take - left) if x)
                if not win(tuple(sorted(rest))): return True
    return False
def parts(n, mx):
    if n == 0: yield (); return
    for k in range(min(n, mx), 0, -1):
        for p in parts(n - k, k): yield (k,) + p
agree = total = 0
for n in range(1, 13):
    for p in parts(n, n):
        x = 0
        for r in p: x ^= G[r]
        total += 1; agree += win(tuple(sorted(p))) == (x != 0)
print(f"brute force agrees with the Grundy XOR rule on {agree} of {total} positions (all multisets of rows, <= 12 pins)")
S = [0] * 30
for n in range(1, 30): S[n] = mex({S[n - k] for k in (1, 2) if n - k >= 0})
print(f"control: take 1-2 from the end only gives {S[:9]}... period 3: {all(S[n] == S[n - 3] for n in range(3, 30))} SEEN")
held = max(irr) == 70 and all(g > 0 for g in G[1:]) and agree == total
print("PREDICTION HELD for (a) and (c); (b) held only under the standard reading - as I first wrote it, it FAILED" if held else "PREDICTION FAILED")
json.dump({"G": G[:200], "last_irregular": max(irr)}, open(D / "kayles.json", "w"), separators=(",", ":"))
