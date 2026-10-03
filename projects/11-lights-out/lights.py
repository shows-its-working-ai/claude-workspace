"""Lights Out on 5x5, solved exactly with linear algebra over GF(2) (cycle 98).
Pressing a cell toggles it and its up/down/left/right neighbours. A board b is solvable iff b is in the column space
of the 25x25 press matrix A; the presses x solve A x = b (mod 2). Pressing is commutative and pressing twice cancels,
so a solution is a SET of cells, and the fewest presses is the lightest solution.
Prediction (written first, about the mathematics): A has rank 23 over GF(2), so exactly 2^23 of the 2^25 boards
(one quarter) are solvable, and each solvable board has exactly 2^2 = 4 solutions. Checked two ways: by the rank,
and by brute force over every one of the 2^25 = 33,554,432 boards (each press set gives one board; count the boards hit)."""
import itertools
import numpy as np
N = 5
def press_vec(r, c):
    v = 0
    for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < N and 0 <= cc < N: v |= 1 << (rr * N + cc)
    return v
COLS = [press_vec(r, c) for r in range(N) for c in range(N)]       # column i = effect of pressing cell i (bitmask)

def rank_gf2(vectors):
    basis = []                                                       # standard xor basis
    for v in vectors:
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    return len(basis)

def solve(board):
    """all press sets x (as bitmasks) with A x = board, via Gaussian elimination; returns list (0 or 4 entries)."""
    kern = []
    basis2 = {}
    for i in range(N * N):
        v, pr = COLS[i], 1 << i
        for bit in sorted(basis2, reverse=True):
            if v >> bit & 1: bv, bp = basis2[bit]; v ^= bv; pr ^= bp
        if v: basis2[v.bit_length() - 1] = (v, pr)
        else: kern.append(pr)
    v, pr = board, 0
    for bit in sorted(basis2, reverse=True):
        if v >> bit & 1: bv, bp = basis2[bit]; v ^= bv; pr ^= bp
    if v: return []
    sols = []
    for k in range(1 << len(kern)):
        x = pr
        for j, kv in enumerate(kern):
            if k >> j & 1: x ^= kv
        sols.append(x)
    return sols

def apply(presses):
    b = 0
    for i in range(N * N):
        if presses >> i & 1: b ^= COLS[i]
    return b

if __name__ == "__main__":
    r = rank_gf2(COLS)
    print("rank over GF(2):", r)
    # brute force: image of all 2^25 press sets (vectorised: board = XOR of chosen columns)
    cols = np.array(COLS, dtype=np.int64)
    seen = np.zeros(1 << 25, dtype=np.uint8)
    idx = np.arange(1 << 20, dtype=np.int64)
    low = np.zeros(1 << 20, dtype=np.int64)
    for i in range(20): low ^= np.where(idx >> i & 1, cols[i], 0)
    for hi in range(1 << 5):
        h = 0
        for j in range(5):
            if hi >> j & 1: h ^= COLS[20 + j]
        # np.add.at, not seen[idx] += 1: plain fancy-index += counts a repeated index only ONCE per call (cycle 98)
        np.add.at(seen, low ^ h, 1)
    reachable = int(np.count_nonzero(seen)); multiplicities = set(np.unique(seen[seen > 0]).tolist())
    print(f"brute force: {reachable:,} of {1 << 25:,} boards solvable ({reachable / (1 << 25):.4f}); solutions per solvable board: {sorted(multiplicities)}")
    # cross-check the solver on random boards
    rng = np.random.default_rng(98); bad = 0
    for _ in range(2000):
        b = int(rng.integers(0, 1 << 25)); sols = solve(b)
        if (len(sols) == 4) != bool(seen[b]) or any(apply(x) != b for x in sols): bad += 1
    print("solver vs brute force on 2,000 random boards: mismatches", bad)
    held = r == 23 and reachable == 1 << 23 and multiplicities == {4} and bad == 0
    print("PREDICTION", "HELD" if held else "FAILED")
