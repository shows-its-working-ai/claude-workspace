"""Sim (Gustavus Simmons, 1969): 6 dots, 15 lines; players colour lines in turn; whoever completes a triangle all in
their OWN colour loses. Solved here by memoised search over (mine, theirs) bitmasks, mover first.
Predictions (journal, cycle 213): (a) no game can end in a draw (Ramsey: R(3,3) = 6); (b) from memory, a GUESS: the
second player wins with perfect play. Controls: on FIVE dots a draw IS possible (the pentagon/pentagram colouring) -
must be SEEN; and the solver must agree with a plain unmemoised search on random late positions."""
import itertools, json, random, sys, time
from functools import lru_cache
from pathlib import Path
D = Path(__file__).resolve().parent
sys.setrecursionlimit(10000)

def setup(n):
    E = list(itertools.combinations(range(n), 2)); idx = {e: i for i, e in enumerate(E)}
    T = [(1 << idx[(a, b)]) | (1 << idx[(a, c)]) | (1 << idx[(b, c)]) for a, b, c in itertools.combinations(range(n), 3)]
    return E, T
E, T = setup(6); FULL = (1 << 15) - 1
tri = lambda m: any(m & t == t for t in T)

@lru_cache(maxsize=None)
def wins(mine, theirs):            # the player to move, holding `mine`, wins?
    free = FULL & ~(mine | theirs)
    if not free: return False      # unreachable if (a) holds; checked below
    m = free
    while m:
        b = m & -m; m ^= b
        if not tri(mine | b) and not wins(theirs, mine | b): return True
    return False

t0 = time.time(); first = wins(0, 0); dt = time.time() - t0
print(f"positions solved: {wins.cache_info().currsize} in {dt:.1f}s")
# (a) every complete 2-colouring of K6 has a one-colour triangle
nodraw = all(tri(m) or tri(FULL ^ m) for m in range(1 << 15))
print(f"(a) every colouring of all 15 lines has a one-colour triangle (no draws): {nodraw}")
print(f"(b) GUESS second player wins: {not first}")
E5, T5 = setup(5); full5 = (1 << 10) - 1
draw5 = [m for m in range(1 << 10) if bin(m).count('1') == 5 and not any(m & t == t for t in T5) and not any((full5 ^ m) & t == t for t in T5)]
print(f"control: five dots, colourings with no one-colour triangle: {len(draw5)} {'SEEN' if draw5 else 'NOT SEEN'}")

def plain(mine, theirs):           # no memo, no shortcuts: the definition, straight
    free = [1 << i for i in range(15) if not (mine | theirs) >> i & 1]
    return any(not tri(mine | b) and not plain(theirs, mine | b) for b in free)
rng = random.Random(213); sample, agree = [], 0
while len(sample) < 400:           # random legal positions with 9-11 lines coloured, no triangle yet
    k = rng.randint(9, 11); order = rng.sample(range(15), k); a = b = 0
    for j, e in enumerate(order):
        if j % 2 == 0: a |= 1 << e
        else: b |= 1 << e
    mover, other = (a, b) if k % 2 == 0 else (b, a)
    if tri(a) or tri(b): continue
    sample.append([mover, other, wins(mover, other)]); agree += plain(mover, other) == wins(mover, other)
print(f"memoised == plain search on {len(sample)} random late positions: {agree == len(sample)}")
rng2 = random.Random(7); early = []
while len(early) < 300:            # early/mid positions for the page test (Python's verdicts)
    k = rng2.randint(0, 8); order = rng2.sample(range(15), k); a = b = 0
    for j, e in enumerate(order):
        if j % 2 == 0: a |= 1 << e
        else: b |= 1 << e
    mover, other = (a, b) if k % 2 == 0 else (b, a)
    if tri(a) or tri(b): continue
    early.append([mover, other, wins(mover, other)])
print("PREDICTION HELD" if nodraw and not first else "PREDICTION FAILED")
json.dump({"edges": E, "first_player_wins": first, "positions": sample + early}, open(D / "sim.json", "w"), separators=(",", ":"))
