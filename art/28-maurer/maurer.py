"""Rose Lines: the Maurer rose. Predictions (journal, cycle 229): (a) r = sin(n theta) has n petal tips (n odd) or 2n
(n even), counted as distinct POSITIONS in the plane; (b) the d-degree polygon closes after 360/gcd(360, d) steps.
Control: counting tips of |sin(n theta)| instead gives a different answer for odd n (2n) - SEEN."""
import json, math
from pathlib import Path
D = Path(__file__).resolve().parent

def tips(n, f=math.sin):
    pts = set()
    for k in range(4 * n):                       # |sin(n t)| = 1 exactly at t = (2k+1) pi / (2n)
        t = (2 * k + 1) * math.pi / (2 * n); r = f(n * t)
        pts.add((round(r * math.cos(t), 9) + 0.0, round(r * math.sin(t), 9) + 0.0))
    return len(pts)

def closes(d):
    k, a = 1, d % 360
    while a != 0: a = (a + d) % 360; k += 1
    return k

a = {n: tips(n) for n in range(1, 13)}
ok_a = all(a[n] == (n if n % 2 else 2 * n) for n in a)
print(f"(a) petal tips for n = 1..12: {a}; n odd -> n, n even -> 2n: {ok_a}")
b = {d: closes(d) for d in range(1, 361)}
ok_b = all(b[d] == 360 // math.gcd(360, d) for d in b)
print(f"(b) closing steps == 360/gcd(360, d) for all d = 1..360: {ok_b}; d = 71 -> {b[71]}, 72 -> {b[72]}, 29 -> {b[29]}")
ctl = {n: tips(n, lambda x: abs(math.sin(x))) for n in (3, 5)}
print(f"control: |sin| tips for n = 3, 5: {ctl} (vs {a[3]}, {a[5]}) {'SEEN' if ctl[3] != a[3] and ctl[5] != a[5] else 'NOT SEEN'}")
print("PREDICTION HELD" if ok_a and ok_b else "PREDICTION FAILED")
json.dump({"tips": a, "closes": b}, open(D / "maurer.json", "w"), separators=(",", ":"))
