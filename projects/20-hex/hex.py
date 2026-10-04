"""Hex on n x n (cycle 180). Cell i = r*n + c. Red (1) joins row 0 to row n-1; Blue (2) joins column 0 to n-1.
Neighbours on the rhombus: (r,c+-1), (r+-1,c), (r-1,c+1), (r+1,c-1)."""
import json, sys
from functools import lru_cache
from pathlib import Path
sys.setrecursionlimit(10000)
def nbrs(n):
    out = []
    for i in range(n * n):
        r, c = divmod(i, n)
        out.append([rr * n + cc for rr, cc in ((r, c - 1), (r, c + 1), (r - 1, c), (r + 1, c), (r - 1, c + 1), (r + 1, c - 1))
                    if 0 <= rr < n and 0 <= cc < n])
    return out
def wins(n, board, who, N):
    start = [i for i in range(n * n) if board[i] == who and (i // n == 0 if who == 1 else i % n == 0)]
    seen, stack = set(start), list(start)
    while stack:
        i = stack.pop()
        if (i // n == n - 1) if who == 1 else (i % n == n - 1): return True
        for j in N[i]:
            if board[j] == who and j not in seen: seen.add(j); stack.append(j)
    return False
out = {}
for n in (3, 4):
    N = nbrs(n); bad = 0
    for m in range(1 << (n * n)):
        b = [1 if m >> i & 1 else 2 for i in range(n * n)]
        bad += wins(n, b, 1, N) == wins(n, b, 2, N)          # both or neither
    @lru_cache(None)
    def value(board, who):                                      # +1 if `who` (to move) wins with perfect play
        b = list(board)
        for i in range(n * n):
            if b[i] == 0:
                b[i] = who
                if wins(n, b, who, N) or value(tuple(b), 3 - who) < 0: return 1
                b[i] = 0
        return -1
    empty = (0,) * (n * n)
    first = [i for i in range(n * n) if (lambda b: wins(n, b, 1, N) or value(tuple(b), 2) < 0)([1 if j == i else 0 for j in range(n * n)])]
    out[n] = first
    print(f"{n}x{n}: fillings with not exactly one winner: {bad} of {1 << (n * n)}; first player wins: {value(empty, 1) == 1}; "
          f"winning first moves (cells r,c): {[divmod(i, n) for i in first]}")
    value.cache_clear()
(Path(__file__).resolve().parent / "hex.json").write_text(json.dumps(out), encoding="utf-8")
