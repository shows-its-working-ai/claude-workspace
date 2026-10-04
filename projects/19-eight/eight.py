"""The 8-puzzle by breadth-first search from solved (cycle 172). Blank = 0, solved = 123456780."""
from collections import Counter, deque
from itertools import permutations
SOLVED = "123456780"
NB = {i: [j for j in (i - 3, i + 3, i - 1, i + 1) if 0 <= j < 9 and (abs(j - i) == 3 or j // 3 == i // 3)] for i in range(9)}
dist = {SOLVED: 0}; q = deque([SOLVED])
while q:
    s = q.popleft(); b = s.index("0")
    for j in NB[b]:
        t = list(s); t[b], t[j] = t[j], t[b]; t = "".join(t)
        if t not in dist: dist[t] = dist[s] + 1; q.append(t)
def inversions(s): a = [c for c in s if c != "0"]; return sum(a[i] > a[j] for i in range(8) for j in range(i + 1, 8))
allp = ["".join(p) for p in permutations("012345678")]
parity_ok = all((inversions(p) % 2 == 0) == (p in dist) for p in allp)
far = max(dist.values()); hard = sorted(s for s, d in dist.items() if d == far)
print(f"arrangements {len(allp)}, reachable {len(dist)}, farthest {far}, positions that far: {len(hard)} {hard}")
print(f"even number of inversions <=> reachable, on all {len(allp)}: {parity_ok}")
print("distance counts:", dict(sorted(Counter(dist.values()).items())))
print("PREDICTION HELD" if (len(dist), far, len(hard)) == (181440, 31, 2) else "PREDICTION FAILED")
