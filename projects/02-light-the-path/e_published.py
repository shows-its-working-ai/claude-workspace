"""Cycle 64: is my E-speed ladder (cycle 56) the published E^n family?
Published data (Martinez, McIntosh, Seck Tuoh Mora, arXiv 0706.3348, appendix A.11): 16 phase strings for the
E glider (variants A-D x phases f1-f4, mostly 19 cells), written with the ether as "11111000100110" (a rotation of my
"00010011011111"). The paper says E^n "can arbitrarily extend ... to the right with E".
Prediction (written first): (control) a lone E's raw row contains exactly ONE published E string at some phase;
and each rung of my ladder contains a run of published E strings placed back to back, one longer per rung.
Method: pure string matching on the raw rows at all 30 phases; no simulation of the paper's strings needed."""
import re
import numpy as np
TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
step = lambda r: TABLE[4 * np.roll(r, 1) + 2 * r + np.roll(r, -1)]
NT = 60; W = 14 * NT; base = np.tile(TILE, NT); L0 = 14 * 30
SHIFT = next(d for d in range(W) if np.array_equal(np.roll(base, d), step(base)))
E_STRINGS = """1111100000000100110 1111100010000000110 1111100010011000000 1110000011000100110
1111101000011100110 1111100011100011010 111110001001101001111111000100110
1111101100000100110 1111100011110000110 1111100010011001000 1110110011000100110
1111101111011100110 1111100011100111010 1111100010011010110 1111111111000100110""".split()
EBAR_STRINGS = """111110000100011111010 111110001000110011000 11111000100110011101110011000100110 111011011101011100110
111110111111011111010 111110001110000111000 11111000100110100011010011000100110 111110011111011100110
111110001011000111010 111110001001111100110 11111000100110110001011111000100110 111111001111000100110""".split()
ETHER_PAPER = "11111000100110"
assert ETHER_PAPER in "".join(map(str, TILE)) * 2, "paper ether is a rotation of mine"

def evolve(row, n):
    for _ in range(n): row = step(row)
    return row
def collision_object():                                         # cycle 54/56: E hit by G (sep 4, delay 4)
    row = base.copy(); row[L0 + 6] ^= 1
    for t in range(3600):
        if t == 4:
            for o in (2, 18): row[(L0 + 14 * 4 + o + SHIFT * t) % W] ^= 1
        row = step(row)
    return row
def rung(obj, m, k):                                             # cycle 56 surgery (raw row only)
    if k > 0: return np.r_[obj[:m], np.tile(obj[m:m + 14], k), obj[m:]]
    if k < 0: return np.r_[obj[:m], obj[m - 14 * k:]]
    return obj
def longest_run(row, phases=30, STR=None):
    """max number of published E strings found back to back (exact concatenation) over all phases"""
    STR = STR or E_STRINGS
    alt = "|".join(sorted(STR, key=len, reverse=True))
    best = 0
    for _ in range(phases):
        s = "".join(map(str, row)); s = s + s[:200]               # ring: allow wrap
        for m in re.finditer(f"(?:{alt})+", s):
            run = m.group(0); n = 0; i = 0                        # count pieces greedily
            while i < len(run):
                for e in sorted(STR, key=len, reverse=True):
                    if run.startswith(e, i): i += len(e); n += 1; break
                else: break
            best = max(best, n)
        row = step(row)
    return best

lone = evolve(np.r_[base[:L0 + 6], [base[L0 + 6] ^ 1], base[L0 + 7:]], 900)
print("CONTROL lone E: longest back-to-back run of published E strings =", longest_run(lone))
print("CONTROL pure ether (should be 0):", longest_run(base.copy()))
obj = collision_object()
x = np.nonzero(obj != evolve(base.copy(), 3600))[0]; m = int(x.min()) + 1
for k in (-2, -1, 0, 1, 2, 3):
    r = rung(obj, m, k); print(f"rung k={k:+d}: longest run = {longest_run(r)}")

# step 3: the E-bar strings (A-C variants, appendix A.12), same matching
def hits(row, STR, phases=30):
    """which published strings occur in the raw row at any of the phases"""
    found = set()
    for _ in range(phases):
        t = "".join(map(str, row)); t += t[:200]
        found |= {x for x in STR if x in t}; row = step(row)
    return found
print()
print("E-BAR: lone glider contains", len(hits(lone, EBAR_STRINGS)), "of", len(EBAR_STRINGS), "published E-bar strings;",
      "pure ether contains", len(hits(base.copy(), EBAR_STRINGS)))
print("E (period 15): lone glider contains", len(hits(lone, E_STRINGS)), "of", len(E_STRINGS))
for k in (-2, -1, 0, 1, 2, 3):
    r = rung(obj, m, k)
    print(f"rung k={k:+d}: E-bar strings present {len(hits(r, EBAR_STRINGS))}/{len(EBAR_STRINGS)}, longest back-to-back E-bar run {longest_run(r, STR=EBAR_STRINGS)}")
