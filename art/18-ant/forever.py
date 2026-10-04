"""A finite certificate that Langton's ant's highway goes on forever (cycle 176).
R = squares (relative to the ant) read during one P-step round; shift = the ant's move per round.
For a square at offset o in round k's window, look back: the most recent round that also had it in its window is
i rounds earlier, where i = the smallest i >= 1 with o + i*shift in R (if any).
  * If some i exists (i <= I), the square's colour is whatever round k-i left there.
  * If none exists, no highway round ever touched it: it must be white from the start.
So if (1) rounds k0 .. k0+I+1 all start with the same heading and colours on R (checked by simulation), and (2) every
never-touched square is white for every round from k0 on (checked until it lies beyond all ink), then every round
after k0+I+1 also starts the same way, by induction: the highway never ends."""
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
P, FIRST = 104, 9977 - 1
black, x, y, d, hist = set(), 0, 0, 0, []
for t in range(14000):
    hist.append((x, y, d, frozenset(black) if t >= FIRST else None))   # state before step t+1
    if (x, y) in black: d = (d - 1) % 4; black.discard((x, y))
    else: d = (d + 1) % 4; black.add((x, y))
    x += DIRS[d][0]; y += DIRS[d][1]
def window(t): x0, y0 = hist[t][:2]; return {(hist[t + i][0] - x0, hist[t + i][1] - y0) for i in range(P)}
def colours(t, R): x0, y0, d0, b = hist[t]; return d0, frozenset(o for o in R if (x0 + o[0], y0 + o[1]) in b)
def certificate(t0, extra=frozenset()):
    R = window(t0); sh = (hist[t0 + P][0] - hist[t0][0], hist[t0 + P][1] - hist[t0][1])
    look = {}
    for o in R:
        for i in range(1, 200):
            if (o[0] + i * sh[0], o[1] + i * sh[1]) in R: look[o] = i; break
    I = max(look.values())
    if t0 + (I + 2) * P >= len(hist): return None
    ref = colours(t0, R)
    if any(window(t0 + k * P) != R or colours(t0 + k * P, R) != ref for k in range(1, I + 2)): return None
    x0, y0, _, b0 = hist[t0]; ink = b0 | extra; xs = [c[0] for c in ink]; ys = [c[1] for c in ink]   # box of ALL ink
    for o in R:
        if o in look: continue
        for k in range(0, 10 ** 6):                       # this square in round k0+k; white until beyond all ink
            c = (x0 + o[0] + k * sh[0], y0 + o[1] + k * sh[1])
            if not (min(xs) <= c[0] <= max(xs) and min(ys) <= c[1] <= max(ys)): break
            if c in ink: return None
    return sh, I, len(R), sum(o not in look for o in R)
for t0 in range(FIRST, FIRST + 2000):
    c = certificate(t0)
    if c: print(f"certificate: round starting at step {t0 + 1}; shift {c[0]}; window {c[2]} squares, {c[3]} never touched before; checked rounds {t0 + 1}..{t0 + 1 + (c[1] + 1) * P} (I = {c[1]})"); break
else: print("no certificate found")
# control: plant one dark square on the highway's future path (well inside the ink's box); the certificate must fail
x0, y0 = hist[t0][:2]; R = window(t0); sh0 = (hist[t0 + P][0] - x0, hist[t0 + P][1] - y0)
o = next(o for o in sorted(R) if all((o[0] + i * sh0[0], o[1] + i * sh0[1]) not in R for i in range(1, 50)))
plant = (x0 + o[0] + 3 * sh0[0], y0 + o[1] + 3 * sh0[1])
print(f'control: dark square planted at {plant} -> certificate', 'FOUND (BLIND!)' if certificate(t0, frozenset([plant])) else 'refused (good)')
print("PREDICTION HELD" if c else "PREDICTION FAILED")
