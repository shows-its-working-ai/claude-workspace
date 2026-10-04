"""Shepard tone model (cycle 196). Voice k at phase p in [0,1): log2 f = log2(F_LOW) + k + p, k = 0..7. Loudness
w = exp(-(log2(f) - C)^2 / (2 s^2)), C = centre of the 8-octave band, s = 1.2 octaves."""
from math import exp, log2
F_LOW, K, S = 27.5, 8, 1.2
C = log2(F_LOW) + K / 2
def voices(p): return [log2(F_LOW) + k + p for k in range(K)]
def weight(l): return exp(-(l - C) ** 2 / (2 * S * S))
def centroid(p): v = voices(p); w = [weight(x) for x in v]; return sum(a * b for a, b in zip(v, w)) / sum(w)
cycle = sorted(round(2 ** x, 6) for x in voices(1.0)[:-1]) == sorted(round(2 ** x, 6) for x in voices(0.0)[1:])
up = all(b > a for a, b in zip([voices(i / 1000)[k] for i in range(1000) for k in [3]], [voices((i + 1) / 1000)[3] for i in range(1000)]))
cs = [centroid(i / 1000) for i in range(1001)]
drift = max(cs) - min(cs)
print(f"(1) after one cycle the voices are the starting set: {cycle}")
print(f"(2) a voice only rises within a cycle: {up}")
print(f"(3) weighted mean pitch drifts {drift:.4f} octaves over a cycle (< 0.25 predicted)")
S0 = S; S = 0.3                                          # control: a much narrower bell should let the pitch wobble
cn = [centroid(i / 1000) for i in range(1001)]; S = S0; cdrift = max(cn) - min(cn)
print(f"control: with a 0.3-octave bell the mean pitch drifts {cdrift:.3f} octaves", "SEEN" if cdrift > 0.25 else "BLIND")
print("(1) and (2) are nearly true by construction; the real test is the page's rendered audio (test.py).")
print("PREDICTION HELD" if cycle and up and drift < 0.25 and cdrift > 0.25 else "PREDICTION FAILED")
