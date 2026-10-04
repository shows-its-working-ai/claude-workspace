"""Brute-force check of Euler's one-stroke rule on every graph with 2..6 points (cycle 181)."""
from itertools import combinations
def trails(n, edges):                                       # all endpoints (start, end) of trails using every edge once
    adj = {v: [] for v in range(n)}
    for k, (a, b) in enumerate(edges): adj[a].append((b, k)); adj[b].append((a, k))
    ends, used = set(), [False] * len(edges)
    def go(v, s, left):
        if not left: ends.add((s, v)); return
        for w, k in adj[v]:
            if not used[k]: used[k] = True; go(w, s, left - 1); used[k] = False
    for s in range(n):
        if adj[s]: go(s, s, len(edges))
    return ends
def connected(n, edges):
    vs = {v for e in edges for v in e}
    if not vs: return False
    seen, st = {min(vs)}, [min(vs)]
    while st:
        v = st.pop()
        for a, b in edges:
            for x, y in ((a, b), (b, a)):
                if x == v and y not in seen: seen.add(y); st.append(y)
    return seen == vs
bad = checked = 0
for n in range(2, 7):
    pairs = list(combinations(range(n), 2))
    for m in range(1, 1 << len(pairs)):
        edges = [p for i, p in enumerate(pairs) if m >> i & 1]
        if not connected(n, edges): continue
        checked += 1
        odd = [v for v in range(n) if sum(v in e for e in edges) % 2]
        ends = trails(n, edges)
        rule = len(odd) in (0, 2)
        if bool(ends) != rule: bad += 1
        elif len(odd) == 2 and any({s, t} != set(odd) for s, t in ends): bad += 1
print(f"connected graphs checked: {checked}; disagreements with the rule: {bad}")
print("PREDICTION HELD" if bad == 0 else "PREDICTION FAILED")
