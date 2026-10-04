"""Hypotrochoid facts (cycle 193). Also provable: |p(t)|^2 = (R-r)^2 + d^2 + 2(R-r)d cos(R t / r), which peaks when
R t / r is a whole turn; over the r/g trips of a closed curve that is exactly R/g times, hence R/g lobes. x(t) = (R-r)cos t + d cos((R-r)t/r), y(t) = (R-r)sin t - d sin((R-r)t/r),
t = angle of the wheel's centre round the ring; one trip = 2*pi."""
from math import cos, sin, pi, gcd, hypot
def pt(R, r, d, t): k = (R - r) / r; return ((R - r) * cos(t) + d * cos(k * t), (R - r) * sin(t) - d * sin(k * t))
bad, N = [], 0
for R in range(2, 41):
    for r in range(1, R):
        d = 0.6 * r; g = gcd(R, r); trips = r // g; N += 1
        x0, y0 = pt(R, r, d, 0)
        back = [m for m in range(1, trips + 1) if hypot(*(a - b for a, b in zip(pt(R, r, d, 2 * pi * m), (x0, y0)))) < 1e-6]
        if back[:1] != [trips]: bad.append((R, r, "closes", back[:1], trips)); continue
        S = 4000 * trips; rad = [hypot(*pt(R, r, d, 2 * pi * trips * i / S)) for i in range(S)]
        # cycle 193: v1 required each sampled peak within 1e-6 of the true max; with few samples per lobe they miss by
        # more (77 false failures). |p|^2 = (R-r)^2 + d^2 + 2(R-r)d cos(R t / r), so every local max of the radius is a
        # true lobe: count local maxima above the midpoint of the radius range instead.
        mid = (max(rad) + min(rad)) / 2; lobes = sum(1 for i in range(S) if rad[i] > rad[i - 1] and rad[i] >= rad[(i + 1) % S] and rad[i] > mid)
        if lobes != R // g: bad.append((R, r, "lobes", lobes, R // g))
def lobes_of(R, r):
    d = 0.6 * r; trips = r // gcd(R, r); S = 4000 * trips; rad = [hypot(*pt(R, r, d, 2 * pi * trips * i / S)) for i in range(S)]
    mid = (max(rad) + min(rad)) / 2; return sum(1 for i in range(S) if rad[i] > rad[i - 1] and rad[i] >= rad[(i + 1) % S] and rad[i] > mid)
c = (lobes_of(12, 8), lobes_of(12, 5))
print(f"control: R=12 r=8 gives {c[0]} lobes, R=12 r=5 gives {c[1]}", "SEEN" if c == (3, 12) else "BLIND")
print(f"gear pairs checked: {N}; failures: {len(bad)}", bad[:5])
print("PREDICTION HELD" if not bad else "PREDICTION FAILED")
