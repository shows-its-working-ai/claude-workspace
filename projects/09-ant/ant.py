"""Langton's ant, reference implementation (cycle 86).
Rules: on a white cell turn right, on a black cell turn left; flip the cell; step forward. Start: empty grid, facing up.
The highway: after a chaotic phase the ant repeats a 104-step cycle that moves it 2 cells diagonally.
Onset = the first step t such that the ant's sequence of turns from t onward is periodic with period 104 (checked over
a long window), AND it stays so. We find the earliest t where turns[t:t+W] == turns[t+104:t+104+W].
Prediction (written first): onset is between step 9,000 and 11,000."""
import sys

def run(steps):
    x = y = 0; d = 0                                   # 0 up, 1 right, 2 down, 3 left
    black = set(); turns = []
    for _ in range(steps):
        if (x, y) in black: d = (d - 1) % 4; black.discard((x, y)); turns.append("L")
        else: d = (d + 1) % 4; black.add((x, y)); turns.append("R")
        x += (0, 1, 0, -1)[d]; y += (-1, 0, 1, 0)[d]
    return turns, black, (x, y)

def onset(turns, period=104, window=2000):
    """earliest t from which the turn sequence repeats with this period for `window` steps"""
    s = "".join(turns)
    for t in range(0, len(s) - period - window):
        if s[t:t + window] == s[t + period:t + period + window]:
            return t
    return None

if __name__ == "__main__":
    turns, black, pos = run(16000)
    t = onset(turns)
    print(f"highway onset at step {t}; after 16000 steps: {len(black)} black cells, ant at {pos}")
    alt = [onset(turns, window=w) for w in (500, 1000, 4000)]
    print("onset with comparison windows 500 / 1000 / 4000:", alt)
    print("PREDICTION", "HELD" if t is not None and 9000 <= t <= 11000 else "FAILED", "(9,000-11,000)")
