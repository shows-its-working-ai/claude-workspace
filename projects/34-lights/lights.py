"""Lights Out (cycle 267): pressing a cell toggles it and its up/down/left/right neighbours. Over GF(2) a board is
solvable exactly when it lies in the column space of the 25x25 press matrix. Prediction (before running): rank 23,
so 2^23 of the 2^25 boards (one in four) can be solved. Also: the two 'quiet patterns' (press sets that change
nothing) found by brute force over all 2^25 press sets agree with the null space, and a solver built here solves
every board it says is solvable. Writes lights.json for the page test."""
import itertools, json, random
from pathlib import Path
N = 5; D = Path(__file__).resolve().parent
def mask(r, c):
    m = 0
    for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < N and 0 <= cc < N: m |= 1 << (rr * N + cc)
    return m
COLS = [mask(i // N, i % N) for i in range(N * N)]
def solve(board):
    """Gaussian elimination over GF(2): find presses p with XOR of COLS[i] for i in p == board, or None."""
    rows = [(COLS_T[i], (board >> i) & 1) for i in range(N * N)]   # equation per cell: which presses touch it
    piv = []; rows = [list(r) for r in rows]; col_of = {}
    r = 0
    for c in range(N * N):
        sel = next((k for k in range(r, len(rows)) if rows[k][0] >> c & 1), None)
        if sel is None: continue
        rows[r], rows[sel] = rows[sel], rows[r]
        for k in range(len(rows)):
            if k != r and rows[k][0] >> c & 1: rows[k][0] ^= rows[r][0]; rows[k][1] ^= rows[r][1]
        col_of[r] = c; r += 1
    if any(rows[k][0] == 0 and rows[k][1] for k in range(r, len(rows))): return None, r
    presses = 0
    for k, c in col_of.items():
        if rows[k][1]: presses |= 1 << c
    return presses, r
# row i of the system: cell i is toggled by press j iff COLS[j] has bit i (the matrix is symmetric, but don't rely on it)
COLS_T = [sum(((COLS[j] >> i) & 1) << j for j in range(N * N)) for i in range(N * N)]
apply = lambda presses: __import__("functools").reduce(lambda a, j: a ^ COLS[j], [j for j in range(N * N) if presses >> j & 1], 0)
_, rank = solve(0)
print(f"rank of the 25x25 press matrix over GF(2): {rank}; prediction 23: {'HELD' if rank == 23 else 'FAILED'}")
print(f"solvable boards: 2^{rank} of 2^25 = one in {2 ** (25 - rank)}")
# the quiet patterns, found WITHOUT the algebra: the top row's presses decide every other press (chase the lights
# down), so trying all 2^5 top rows finds every press set that leaves an empty board empty
def chase(top):
    presses, lights = 0, 0
    for c in range(N):
        if top >> c & 1: presses |= 1 << c; lights ^= COLS[c]
    for r in range(1, N):
        for c in range(N):
            if lights >> ((r - 1) * N + c) & 1: presses |= 1 << (r * N + c); lights ^= COLS[r * N + c]
    return presses, lights
quiets = [chase(t)[0] for t in range(1, 32) if chase(t)[1] == 0]
print(f"quiet patterns found by trying all 32 top rows and chasing: {len(quiets)} (null space of size 2^{25 - rank} - 1 = {2 ** (25 - rank) - 1})")
rnd = random.Random(267); bad = 0; tried = 0
for _ in range(4000):
    b = rnd.getrandbits(25); p, _ = solve(b)
    if p is not None:
        tried += 1; bad += apply(p) != b
frac = tried / 4000
print(f"random boards: {tried}/4000 solvable ({frac:.3f}, expect 0.25); every solution checked by pressing it: {'yes' if bad == 0 else f'{bad} WRONG'}")
# control: a single lit corner is NOT solvable on 5x5 (it isn't in the column space), a lit centre IS
corner, _ = solve(1); centre, _ = solve(1 << 12)
print(f"control: one lit corner solvable? {corner is not None}; one lit centre solvable? {centre is not None}  {'SEEN' if (corner is None) != (centre is None) else 'NOT SEEN'}")
json.dump({"rank": rank, "quiets": quiets, "cols": COLS}, open(D / "lights.json", "w"))
ok = rank == 23 and len(quiets) == 3 and bad == 0 and abs(frac - 0.25) < 0.03 and (corner is None) != (centre is None)
print("VERDICT: lights check out" if ok else "VERDICT: PROBLEM"); raise SystemExit(0 if ok else 1)
