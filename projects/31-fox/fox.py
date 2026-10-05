"""Find the Fox: shortest plan of looks that is SURE to catch a fox moving to a neighbouring hole each night.
BFS over the set of holes the fox could be in. Predictions (journal, cycle 243): (a) n = 5: 6 looks, e.g. 2,3,4,2,3,4;
(b) GUESS n >= 3: 2(n - 2); (c) n = 1: 1, n = 2: 2. Control: 3,3,3,3,3,3 (always the middle) fails for n = 5 - SEEN."""
import json
from collections import deque
from pathlib import Path
D = Path(__file__).resolve().parent

def step(possible, look, n):
    after = possible - {look}                                    # not where we looked today...
    return frozenset(j for i in after for j in (i - 1, i + 1) if 0 <= j < n) if n > 1 else frozenset()   # ...then it moves

def solve(n):
    start = frozenset(range(n)); seen = {start: []}; q = deque([start])
    while q:
        s = q.popleft()
        for look in range(n):
            if s - {look} == frozenset(): return seen[s] + [look]  # caught today: nowhere else it could be
            t = step(s, look, n)
            if t not in seen: seen[t] = seen[s] + [look]; q.append(t)
    return None

def catches(plan, n):
    s = frozenset(range(n))
    for look in plan:
        if s - {look} == frozenset(): return True
        s = step(s, look, n)
    return False

res = {n: solve(n) for n in range(1, 10)}
for n, p in res.items(): print(f"n = {n}: shortest sure plan {len(p)} looks: {[x + 1 for x in p]}")
a = len(res[5]) == 6 and catches([1, 2, 3, 1, 2, 3], 5)
b = all(len(res[n]) == 2 * (n - 2) for n in range(3, 10))
c = len(res[1]) == 1 and len(res[2]) == 2
print(f"(a) n = 5: 6 looks, and 2,3,4,2,3,4 works: {a}\n(b) GUESS 2(n - 2) for n = 3..9: {b}\n(c) n = 1: 1 look, n = 2: 2 looks: {c}")
# cycle 243: my first "wrong" plan, 2,3,4,4,3,2, turned out to WORK on 5 holes (the mirror form is the answer for
# even n). A plan that really can't: always look in the middle hole.
print(f"curiosity: 2,3,4,4,3,2 also catches it on 5 holes: {catches([1, 2, 3, 3, 2, 1], 5)}")
ctl = catches([2] * 6, 5)
print(f"control: looking in the middle hole six times catches it on 5 holes: {ctl} {'SEEN' if not ctl else 'NOT SEEN'}")
print("PREDICTION HELD" if a and b and c else "PREDICTION FAILED")
json.dump({str(n): len(p) for n, p in res.items()}, open(D / "fox.json", "w"))
