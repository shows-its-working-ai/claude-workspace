"""Cycle 1: elementary cellular automata.

1. Group the 256 rules into equivalence classes under mirror (left<->right)
   and complement (0<->1). Literature says there are exactly 88 -> self-check.
2. Rank each class by how incompressible its long-run behaviour is (zlib),
   to see whether a dumb compression metric rediscovers the "interesting"
   rules (30, 45, 110, 54, ...) without being told about them.
"""
import random
import zlib

def mirror(rule):
    out = 0
    for i in range(8):
        l, c, r = (i >> 2) & 1, (i >> 1) & 1, i & 1
        if (rule >> (4 * r + 2 * c + l)) & 1:
            out |= 1 << i
    return out

def complement(rule):
    out = 0
    for i in range(8):
        if not (rule >> (7 - i)) & 1:
            out |= 1 << i
    return out

def classes():
    seen, groups = set(), []
    for r in range(256):
        if r in seen:
            continue
        orbit = {r, mirror(r), complement(r), mirror(complement(r))}
        seen |= orbit
        groups.append(sorted(orbit))
    return groups

def run(rule, cells, steps):
    n = len(cells)
    rows = [cells]
    for _ in range(steps):
        c = rows[-1]
        rows.append([(rule >> (4 * c[i - 1] + 2 * c[i] + c[(i + 1) % n])) & 1
                     for i in range(n)])
    return rows

# width must NOT be a power of 2: additive (XOR) rules annihilate on 2^k rings.
def complexity(rule, width=257, steps=512, seeds=4):
    """Compressed size of the last half of the run, averaged over random starts,
    normalised so a coin-flip grid scores ~1.0."""
    scores = []
    for s in range(seeds):
        rng = random.Random(s)
        rows = run(rule, [rng.randint(0, 1) for _ in range(width)], steps)
        tail = rows[steps // 2:]
        raw = bytes(b for row in tail for b in row)
        noise = bytes(rng.randint(0, 1) for _ in raw)
        scores.append(len(zlib.compress(raw, 9)) / len(zlib.compress(noise, 9)))
    return sum(scores) / len(scores)

if __name__ == "__main__":
    groups = classes()
    print(f"equivalence classes: {len(groups)}  (expected 88)")
    assert len(groups) == 88
    assert mirror(110) == 124 and complement(110) == 137  # known identities
    scored = sorted(((complexity(g[0]), g) for g in groups), reverse=True)
    print("\nmost incompressible classes:")
    for score, g in scored[:12]:
        print(f"  {score:.3f}  rules {g}")
    print("\nmost compressible classes:")
    for score, g in scored[-5:]:
        print(f"  {score:.3f}  rules {g}")
    with open("ranking.txt", "w") as f:
        for score, g in scored:
            f.write(f"{score:.4f}\t{g}\n")
