"""Towers of Hanoi state graph (cycle 186). A state = tuple, peg of each disk (disk 0 smallest)."""
from collections import deque
def moves(s):
    n = len(s); top = {}
    for d in range(n - 1, -1, -1): top[s[d]] = d                    # smallest disk on each peg
    for a in top:
        for b in range(3):
            if b != a and (b not in top or top[b] > top[a]):
                t = list(s); t[top[a]] = b; yield tuple(t)
def bfs(src):
    dist, cnt = {src: 0}, {src: 1}; q = deque([src])
    while q:
        s = q.popleft()
        for t in moves(s):
            if t not in dist: dist[t] = dist[s] + 1; cnt[t] = cnt[s]; q.append(t)
            elif dist[t] == dist[s] + 1: cnt[t] += cnt[s]
    return dist, cnt
bad = []
for n in range(1, 9):
    A, C = (0,) * n, (2,) * n
    dist, cnt = bfs(A)
    if len(dist) != 3 ** n: bad.append((n, "states"))                 # every one of the 3^n placements is reachable
    if dist[C] != 2 ** n - 1 or cnt[C] != 1: bad.append((n, "A->C", dist[C], cnt[C]))
    if n <= 6:
        diam = max(max(bfs(s)[0].values()) for s in dist)
        if diam != 2 ** n - 1: bad.append((n, "diameter", diam))
    print(f"n={n}: {len(dist)} positions, A->C {dist[C]} moves, {cnt[C]} shortest way(s)" + (f", diameter {diam}" if n <= 6 else ""))
print(f"failures: {bad}")
print("PREDICTION HELD" if not bad else "PREDICTION FAILED")
