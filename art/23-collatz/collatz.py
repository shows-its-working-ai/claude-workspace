"""Collatz Coral: the numbers behind the picture. Predictions (written first, in the journal, cycle 207):
(a) 27 takes 111 steps to reach 1 and peaks at 9232; (b) below 10,000 the longest path starts at 6171, 261 steps;
(c) every n up to 10^6 reaches 1. Control: a deliberately broken rule (3n+3) must be SEEN not to settle at 1."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent

def step(n): return n // 2 if n % 2 == 0 else 3 * n + 1

def path(n, rule=step, cap=10**4):
    out = [n]
    while n != 1 and len(out) <= cap: n = rule(n); out.append(n)
    return out

def steps_upto(lim):
    s = [0] * (lim + 1)
    for n in range(2, lim + 1):
        m, k = n, 0
        while m >= n: m = step(m); k += 1       # every m < n is already known
        s[n] = k + s[m]
    return s

p27 = path(27)
print(f"(a) 27: {len(p27) - 1} steps, peak {max(p27)}")
s = steps_upto(10**6)
best = max(range(1, 10**4), key=lambda n: s[n])
print(f"(b) longest below 10,000: {best}, {s[best]} steps")
top = max(range(1, 10**6 + 1), key=lambda n: s[n])
print(f"(c) all of 1..10^6 reach 1: {len(s) == 10**6 + 1 and all(k > 0 for k in s[2:])} (longest: {top}, {s[top]} steps)")
bad = path(3, rule=lambda n: n // 2 if n % 2 == 0 else 3 * n + 3, cap=50)
print(f"control: rule 3n+3 from 3 settles at 1 within 50 steps: {bad[-1] == 1}; cycles at {bad[-4:]} SEEN" if bad[-1] != 1 else "control: NOT SEEN")
held = len(p27) - 1 == 111 and max(p27) == 9232 and best == 6171 and s[best] == 261
print("PREDICTION HELD" if held else "PREDICTION FAILED")
json.dump({"steps_27": len(p27) - 1, "peak_27": max(p27), "longest_below_10000": best, "longest_steps": s[best],
           "steps_1_to_3000": s[1:3001]}, open(D / "collatz.json", "w"), separators=(",", ":"))
