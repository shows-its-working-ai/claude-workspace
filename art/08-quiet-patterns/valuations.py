"""Cycle 108: where chirality comes from, prime by prime.
In R = GF(2)[s]/(g): u = 1 + (up-down mirror), v = 1 + (left-right mirror). Checks, on every board 1 <= m <= n <= 40:
  (1) u^2 = v^2 = u*v = 0 in R  (so the half-turn's 1 + ab equals u + v exactly), and
  (2) a board has half-turn-only quiet patterns  <=>  at some prime p of g, u and v have the SAME p-valuation k < e
      and u + v has a HIGHER one (their leading terms cancel). Compared with rect.py's solver list."""
import json
from pathlib import Path
from algebra import deg, mul, mod, gcd, shift, chi, q
D = Path(__file__).resolve().parent

def div(a, b):
    r = 0
    while a and deg(a) >= deg(b): sh = deg(a) - deg(b); r |= 1 << sh; a ^= b << sh
    return r
def factor(g):
    out, p = {}, 2
    while deg(g) >= 1:
        if deg(p) > deg(g): break
        while deg(g) >= 1 and mod(g, p) == 0: out[p] = out.get(p, 0) + 1; g = div(g, p)
        p += 1                                       # trial division: composites never divide (their factors are gone)
    return out
def val(x, p, e):
    k = 0
    while k < e and x and mod(x, p) == 0: x = div(x, p); k += 1
    return e if x == 0 else k

if __name__ == "__main__":
    chiral = {(m, n) for m, n, _, _ in json.loads((D / "rect.json").read_text(encoding="utf-8"))["found"]}
    nil = True; agree = True; squares_cancel = 0; boards = 0
    for m in range(1, 41):
        for n in range(m, 41):
            g = gcd(shift(chi(m)), chi(n))
            if deg(g) < 1: continue
            boards += 1
            u, v = 1 ^ mod(shift(q(m)), g), 1 ^ mod(q(n), g)
            nil &= all(mod(mul(a, b), g) == 0 for a, b in ((u, u), (v, v), (u, v)))
            cancel = any(val(u, p, e) == val(v, p, e) < val(u ^ v, p, e) for p, e in factor(g).items())
            agree &= cancel == ((m, n) in chiral)
            squares_cancel += cancel and m == n
    print(f"{boards} boards with quiet patterns")
    print("u^2 = v^2 = uv = 0 on all of them:", nil)
    print("half-turn-only  <=>  leading-term cancellation at some prime:", agree)
    print("squares with a cancellation:", squares_cancel)
    print("VALUATIONS OK" if nil and agree and squares_cancel == 0 else "VALUATIONS FAILED")
