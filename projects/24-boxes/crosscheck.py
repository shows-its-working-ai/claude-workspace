"""Independent check of boxes.py (cycle 195): plain minimax over move sequences with explicit scores (no memo, no
'margin of what's left' trick) on 300 random positions with <= 8 lines left; must equal boxes.py's value()."""
import random
ns = {}; exec(open(__file__.replace("crosscheck.py", "boxes.py"), encoding="utf-8").read().split("v0 = value(0)")[0], ns)
def mm(mask, me, you, turn):                         # final (player0 - player1) with both playing to maximise their own score
    if mask == (1 << 12) - 1: return me - you
    res = []
    for e in range(12):
        if mask >> e & 1: continue
        k = ns["made"](mask, e); t = mask | 1 << e
        if turn == 0: res.append(mm(t, me + k, you, 0 if k else 1))
        else:         res.append(mm(t, me, you + k, 1 if k else 0))
    return max(res) if turn == 0 else min(res)
rng = random.Random(195); bad = 0
for _ in range(300):
    free = rng.randint(1, 8); mask = (1 << 12) - 1
    for e in rng.sample(range(12), free): mask &= ~(1 << e)
    if mm(mask, 0, 0, 0) != ns["value"](mask): bad += 1
from functools import lru_cache
@lru_cache(None)
def wrong(mask):                                       # control: forgets "complete a box, move again"
    if mask == (1 << 12) - 1: return 0
    return max(ns["made"](mask, e) - wrong(mask | 1 << e) for e in range(12) if not mask >> e & 1)
rng2 = random.Random(1950); cb = 0
for _ in range(100):
    mask = (1 << 12) - 1
    for e in rng2.sample(range(12), rng2.randint(3, 8)): mask &= ~(1 << e)
    cb += mm(mask, 0, 0, 0) != wrong(mask)
print(f"control (a solver that forgets the extra move): disagreements {cb}", "SEEN" if cb else "BLIND")
print(f"300 random positions: disagreements {bad}")
print("CROSSCHECK OK" if bad == 0 and cb else "CROSSCHECK FAILED")
