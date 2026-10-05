"""Chomp, solved for every board up to 7 rows x 10 columns. A position is a tuple of row lengths, bottom row first,
non-increasing (a Young diagram); the poison is (0,0). Eating (r,c) cuts every row >= r to length <= c. Whoever eats
the poison loses, so the position (1,) - only the poison left - is a loss for the player to move.
Predictions (journal, cycle 208): (a) every board bigger than 1x1 is a first-player win; (b) nxn: the winning first
move is (1,1); (c) 2xn: the winning first move is the top-right square alone; (d) GUESS: the winning first move is
unique on every board up to 7x10. Control: a solver that forgets the poison rule (eating (0,0) just ends the game as a
WIN) must be SEEN to give a different answer."""
import json
from functools import lru_cache
from pathlib import Path
D = Path(__file__).resolve().parent

def moves(pos):
    for r, length in enumerate(pos):
        for c in range(length):
            if (r, c) == (0, 0): continue
            new = tuple(min(l, c) if i >= r else l for i, l in enumerate(pos))
            yield (r, c), tuple(l for l in new if l)

@lru_cache(maxsize=None)
def wins(pos):                       # True if the player to move wins
    if pos == (1,): return False     # forced to eat the poison
    return any(not wins(p) for _, p in moves(pos))

def winning_moves(rows, cols):
    pos = (cols,) * rows
    return [m for m, p in moves(pos) if not wins(p)]

table = {}
for rows in range(1, 8):
    for cols in range(1, 11):
        if rows * cols == 1: continue
        table[f"{rows}x{cols}"] = winning_moves(rows, cols)

a = all(table[k] for k in table)
b = all(table[f"{n}x{n}"] == [(1, 1)] for n in range(2, 8))
c = all(table[f"2x{n}"] == [(1, n - 1)] for n in range(2, 11))
multi = {k: v for k, v in table.items() if len(v) > 1}
print(f"boards solved: {len(table)}; positions: {wins.cache_info().currsize}")
print(f"(a) every board > 1x1 is a first-player win: {a}")
print(f"(b) nxn (2..7): the only winning move is (1,1): {b}")
print(f"(c) 2xn (2..10): the only winning move is the top-right square: {c}")
print(f"(d) GUESS unique everywhere: {not multi}" + ("" if not multi else f"; FAILED on {len(multi)}: " + ", ".join(f"{k} {v}" for k, v in sorted(multi.items()))))

@lru_cache(maxsize=None)
def wins_broken(pos):                # control: forgets that the poison loses
    if pos == (1,): return True
    return any(not wins_broken(p) for _, p in moves(pos))
diff = sum(wins_broken((c_,) * r_) != wins((c_,) * r_) for r_ in range(1, 5) for c_ in range(1, 6) if r_ * c_ > 1)
print(f"control: broken solver differs on {diff} of 19 small boards {'SEEN' if diff else 'NOT SEEN'}")
print("PREDICTION HELD" if a and b and c else "PREDICTION FAILED")
json.dump({"winning": {k: v for k, v in table.items() if int(k.split('x')[0]) <= 4 and int(k.split('x')[1]) <= 7}},
          open(D / "chomp.json", "w"), separators=(",", ":"))
