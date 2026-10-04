"""Cycle 150: Nim by brute force (memoised minimax: a position is a win if some move reaches a loss) vs Bouton's rule
(win iff XOR of heaps != 0), over 3 heaps of 0..7 and 4 heaps of 0..5."""
from functools import lru_cache, reduce
from itertools import product
@lru_cache(maxsize=None)
def wins(h):                                   # h: sorted tuple; True if the player to move can force taking the last
    return any(not wins(tuple(sorted(h[:i] + (k,) + h[i + 1:]))) for i in range(len(h)) for k in range(h[i]))
def bouton(h): return reduce(lambda a, b: a ^ b, h, 0) != 0
if __name__ == "__main__":
    bad = 0; total = 0
    for heaps, top in ((3, 7), (4, 5)):
        for h in product(range(top + 1), repeat=heaps):
            total += 1; bad += wins(tuple(sorted(h))) != bouton(h)
    print(f"positions checked: {total}; disagreements: {bad}")
    print("PREDICTION", "HELD" if total == 512 + 1296 and bad == 0 else "FAILED", "(XOR rule == brute force)")
