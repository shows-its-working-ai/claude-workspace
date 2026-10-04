"""The Hex 'maze walk' as a program (cycle 194), for the essay writing/31-why-hex-cant-draw.md.
Board n x n, cell (r, c); neighbours (r,c+-1), (r+-1,c), (r-1,c+1), (r+1,c-1). A border ring is added: rows -1 and n
red, columns -1 and n blue (for rows 0..n-1); the 4 corner cells stay uncoloured. Three mutually adjacent cells make a
triangle. Start on the edge between red (-1,0) and blue (0,-1), step into the triangle that holds board cell (0,0),
and keep leaving each triangle by its OTHER red-blue edge until the next triangle touches an uncoloured corner."""
import sys
from itertools import product
ns = {}; exec(open(__file__.replace("walk.py", "hex.py"), encoding="utf-8").read().split("out = {}")[0], ns)
D = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, 1), (1, -1)]
nb = lambda a: {(a[0] + dr, a[1] + dc) for dr, dc in D}
def walk(n, col):                                   # col(cell) -> 1 red, 2 blue, None uncoloured / outside
    a, b, third = (-1, 0), (0, -1), (0, 0)          # a red, b blue, current triangle = {a, b, third}
    for _ in range(10 * n * n + 100):
        t = col(third)
        if t is None: return None
        if t == 1: a_new, b_new = third, b          # exit across the other red-blue edge
        else:      a_new, b_new = a, third
        nxt = [w for w in nb(a_new) & nb(b_new) if w != (a if t == 1 else b)]   # the cell we're leaving behind
        a, b, third = a_new, b_new, nxt[0]
        if col(third) is None:
            corner = third
            return {(-1, n): "top-right", (n, -1): "bottom-left", (n, n): "bottom-right", (-1, -1): "top-left"}.get(corner, f"edge {corner}")
    return "LOOPED"
bad, ends = [], {}
for n in (2, 3, 4):
    N = ns["nbrs"](n)
    for m in range(1 << (n * n)):
        board = [1 if m >> i & 1 else 2 for i in range(n * n)]
        def col(cell, board=board, n=n):
            r, c = cell
            if 0 <= r < n and 0 <= c < n: return board[r * n + c]
            if r in (-1, n) and 0 <= c < n: return 1
            if c in (-1, n) and 0 <= r < n: return 2
            return None
        end = walk(n, col); ends[end] = ends.get(end, 0) + 1
        red = ns["wins"](n, board, 1, N)
        if end not in ("bottom-left", "top-right") or (end == "bottom-left") != red: bad.append((n, m, end, red))
    print(f"n={n}: {1 << (n * n)} fillings walked; disagreements with brute force: {sum(1 for b in bad if b[0] == n)}")
print("where walks ended:", ends)
print("PREDICTION HELD" if not bad else f"PREDICTION FAILED {bad[:3]}")
