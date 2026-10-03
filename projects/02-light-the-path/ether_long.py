"""Do the 'localized' single-flip defects persist (true gliders) over a long run?"""
from levels import run
TILE = [int(c) for c in "00010011011111"]
W, T = 14 * 12, 200
base = TILE * 12
clean = run(110, [], W, T, base=base)
for x in (18, 21, 25, 27, 15, 22):
    hit = run(110, [x + 56], W, T, base=base)      # flip well away from the seam
    out = []
    for t in (28, 80, 140, 199):
        d = [i for i, (a, b) in enumerate(zip(clean[t], hit[t])) if a != b]
        out.append(f"t{t}: n={len(d):3d} span={(d[-1] - d[0] + 1) if d else 0:3d} at={(d[0] if d else '-')}")
    print(f"flip {x}: " + " | ".join(out))
