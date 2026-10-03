"""Cross-check placements() against brute force (all 2^n lines) on random lines and random
partial knowledge. The solver decides what counts as 'fair', so it must be right first."""
import itertools, random
from puzzles import placements, clues
rng = random.Random(7); bad = 0; trials = 0
for _ in range(3000):
    n = rng.randint(1, 10)
    truth = [rng.randint(0, 1) for _ in range(n)]
    clue = clues(truth)
    known = tuple(v if rng.random() < 0.3 else None for v in truth)
    brute = {line for line in itertools.product((0, 1), repeat=n)
             if clues(line) == clue and all(k is None or k == v for k, v in zip(known, line))}
    got = set(placements(clue, n, known))
    trials += 1; bad += got != brute
    assert all(len(l) == n for l in got)
print(f"placements() vs brute force: {trials - bad}/{trials} agree")
print("SOLVER OK" if bad == 0 else "SOLVER BROKEN")
