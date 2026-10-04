"""Polyrhythm facts, exact fractions (cycle 163). Writes against.json: "p,q" -> merged onset numerators over lcm."""
import json
from fractions import Fraction as F
from math import gcd, lcm
from pathlib import Path
bad, out = [], {}
for p in range(1, 13):
    for q in range(1, 13):
        on = sorted({F(i, p) for i in range(p)} | {F(j, q) for j in range(q)})
        gaps = [b - a for a, b in zip(on, on[1:] + [F(1)])]
        if len(on) != p + q - gcd(p, q): bad.append((p, q, "count", len(on)))
        if gaps != gaps[::-1]: bad.append((p, q, "palindrome"))
        if gcd(p, q) == 1 and min(gaps) != F(1, p * q): bad.append((p, q, "min gap", min(gaps)))
        L = lcm(p, q); out[f"{p},{q}"] = [int(t * L) for t in on]
(Path(__file__).resolve().parent / "against.json").write_text(json.dumps(out), encoding="utf-8")
print("3 against 2 merged (sixths):", out["3,2"], " 4 against 3 (twelfths):", out["4,3"])
print(f"pairs checked: {len(out)}; failures: {len(bad)}", bad[:5])
print("PREDICTION HELD" if not bad else "PREDICTION FAILED")
