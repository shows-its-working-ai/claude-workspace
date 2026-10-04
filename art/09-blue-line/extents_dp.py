"""Cycle 113: an independent count of four-bell extents (cycle 112 got 10,792 with a backtracking search).
Different algorithm: layered dynamic programming over (set of rows visited, current row), merging paths that reach
the same state, so it never enumerates extents one by one. Different representation too: rows are indices 0..23
into itertools.permutations, and changes are built as position permutations, not string swaps.
Also counts the no-long-places ones independently: that needs the last two moves of each bell, so for that count
the state also carries the previous row and the first two rows (to check the wrap-around)."""
from itertools import permutations
from collections import defaultdict

ROWS = list(permutations(range(4)))
IDX = {r: i for i, r in enumerate(ROWS)}
CHANGES = [(1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2), (1, 0, 3, 2)]       # position maps: 12, 23, 34, x
ADJ = [[IDX[tuple(r[c[k]] for k in range(4))] for c in CHANGES] for r in ROWS]
ROUNDS = IDX[(0, 1, 2, 3)]
FULL = (1 << 24) - 1

def count_all():
    layer = {(1 << ROUNDS, ROUNDS): 1}
    for _ in range(23):
        nxt = defaultdict(int)
        for (mask, v), c in layer.items():
            for w in ADJ[v]:
                if not mask >> w & 1: nxt[(mask | 1 << w, w)] += c
        layer = nxt
    return sum(c for (mask, v), c in layer.items() if mask == FULL and ROUNDS in ADJ[v])

def still(a, b, c):
    """some bell is in the same position in rows a, b and c (three rows running)"""
    return any(ROWS[a][p] == ROWS[b][p] == ROWS[c][p] for p in range(4))

def count_no_long_places():
    # state: (mask, second row, previous row, current row); rounds is row 0 of the cycle
    layer = defaultdict(int)
    for w in ADJ[ROUNDS]: layer[(1 << ROUNDS | 1 << w, w, ROUNDS, w)] += 1
    for _ in range(22):
        nxt = defaultdict(int)
        for (mask, second, prev, v), c in layer.items():
            for w in ADJ[v]:
                if mask >> w & 1 or still(prev, v, w): continue
                nxt[(mask | 1 << w, second, v, w)] += c
        layer = nxt
    total = 0
    for (mask, second, prev, v), c in layer.items():     # close: v -> rounds -> second, checking the wrap triples
        if mask == FULL and ROUNDS in ADJ[v] and not still(prev, v, ROUNDS) and not still(v, ROUNDS, second):
            total += c
    return total

if __name__ == "__main__":
    a = count_all(); b = count_no_long_places()
    print(f"DP count, all extents from rounds: {a}")
    print(f"DP count, no long places: {b}")
    print("AGREES WITH CYCLE 112" if (a, b) == (10792, 24) else "DISAGREES WITH CYCLE 112")
