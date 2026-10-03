"""Why does the envelope method read slow fifths at 3x? Rebuild the exact measurement in numpy
(same harmonic tones, RBJ constant-0dB bandpass as WebAudio uses, same RMS envelope + mean
up-crossing count) and switch parts on and off.
Hypothesis (written first): higher coincidences (6f1~4f2 at 2b, 9f1~6f2 at 3b) leak through the
filter skirts and the crossing count locks onto the fastest one."""
import numpy as np
from beats import freq

SR = 44100
def tones(f1, f2, dur, ks1=range(1, 10), ks2=range(1, 10)):
    t = np.arange(int(SR * dur)) / SR
    return sum(np.sin(2 * np.pi * k * f1 * t) / k for k in ks1) + sum(np.sin(2 * np.pi * k * f2 * t) / k for k in ks2)

def bandpass(x, f0, Q):
    w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / (2 * Q)
    b0, b2, a0, a1, a2 = al, -al, 1 + al, -2 * np.cos(w0), 1 - al
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    for n, xn in enumerate(x):
        yn = (b0 * xn + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, xn, y1, yn; y[n] = yn
    return y

def envelope_rate(y):
    hop = 441; env = np.sqrt(np.mean(y[: len(y) // hop * hop].reshape(-1, hop) ** 2, axis=1))
    e = env[100:-60]; m = e.mean()
    up = np.nonzero((e[:-1] < m) & (e[1:] >= m))[0]
    return (len(up) - 1) / ((up[-1] - up[0]) / 100) if len(up) > 1 else 0.0, len(up)

lo, b, dur = 53, 0.32, 20
f1 = freq(lo); f2 = (3 * f1 - b) / 2; fc = (3 * f1 + 2 * f2) / 2
print(f"lo={lo} fifth, intended beat {b}/s, filter centre {fc:.2f} Hz, {dur}s\n")
cases = {
  "A only the two coinciding partials (3f1, 2f2), filtered": dict(ks1=[3], ks2=[2]),
  "B all 9 harmonics, filtered (= what the test does)":    dict(),
  "C all harmonics EXCEPT 6f1/4f2 and 9f1/6f2":             dict(ks1=[1, 2, 3, 4, 5, 7, 8], ks2=[1, 2, 3, 5]),
  "D only 3f1 + 2f2 + 9f1 + 6f2 (the 3b pair added)":      dict(ks1=[3, 9], ks2=[2, 6]),
  "E only 3f1 + 2f2 + 6f1 + 4f2 (the 2b pair added)":      dict(ks1=[3, 6], ks2=[2, 4]),
}
for name, kw in cases.items():
    y = bandpass(tones(f1, f2, dur, **kw), fc, 30)
    r, n = envelope_rate(y)
    print(f"{name:58s} -> {r:.3f}/s  ({n} up-crossings)  = {r / b:.2f} x intended")

# --- Hypothesis 2 (after hypothesis 1 was falsified by case A): CHATTER. The 10 ms RMS window
# holds a non-integer number of ~524 Hz cycles, so the envelope carries a small ripple; a SLOW
# beat dwells near the mean and the ripple makes it cross several times. Prediction: hysteresis
# (count an up-crossing only after dipping below mean - h and rising above mean + h) fixes it.
def envelope_rate_hyst(y, frac=0.15):
    hop = 441; env = np.sqrt(np.mean(y[: len(y) // hop * hop].reshape(-1, hop) ** 2, axis=1))
    e = env[100:-60]; m = e.mean(); h = frac * (e.max() - e.min())
    up, armed = [], False
    for i, v in enumerate(e):
        if v < m - h: armed = True
        elif v > m + h and armed: up.append(i); armed = False
    return (len(up) - 1) / ((up[-1] - up[0]) / 100) if len(up) > 1 else 0.0, len(up)

print("\nwith hysteresis:")
for name, kw in list(cases.items())[:2]:
    y = bandpass(tones(f1, f2, dur, **kw), fc, 30)
    r, n = envelope_rate_hyst(y)
    print(f"{name:58s} -> {r:.3f}/s  ({n} up-crossings)  = {r / b:.2f} x intended")
for lo2, b2 in [(56, 0.44), (53, 0.68), (60, 0.886)]:
    g1 = freq(lo2); g2 = (3 * g1 - b2) / 2
    y = bandpass(tones(g1, g2, dur), (3 * g1 + 2 * g2) / 2, 30)
    r0, _ = envelope_rate(y); r1, _ = envelope_rate_hyst(y)
    print(f"lo={lo2} b={b2}: no hysteresis {r0:.3f} ({r0 / b2:.2f}x) | hysteresis {r1:.3f} ({r1 / b2:.2f}x)")
