"""Cycle 87: does every start end in a highway? (Observed, never proved.)
Prediction (written first): 100 random starts (a 10x10 patch, each cell black with probability 0.3, ant in the
middle facing up) ALL reach a highway within 200,000 steps, and the median onset is above 10,000.
Detection, as on the page: the last 2,000 turns must repeat with period 104; then walk back to the first step of
the repetition. Control: the empty grid must give 9,977."""
import random, statistics

def onset_of(black, limit=200_000, period=104, win=2000, check_every=5000):
    x = y = 0; d = 0; turns = bytearray()
    for n in range(1, limit + 1):
        if (x, y) in black: d = (d - 1) % 4; black.discard((x, y)); turns.append(0)
        else: d = (d + 1) % 4; black.add((x, y)); turns.append(1)
        x += (0, 1, 0, -1)[d]; y += (-1, 0, 1, 0)[d]
        if n % check_every == 0 and n >= period + win:
            e = n - period - win
            if turns[e:e + win] == turns[e + period:e + period + win]:
                t = e
                while t > 0 and turns[t - 1] == turns[t - 1 + period]: t -= 1
                return t
    return None

if __name__ == "__main__":
    ctrl = onset_of(set())
    print("CONTROL empty grid:", ctrl, "OK" if ctrl == 9977 else "MISMATCH")
    rng = random.Random(87); res = []
    for k in range(100):
        black = {(x, y) for x in range(-5, 5) for y in range(-5, 5) if rng.random() < 0.3}
        res.append(onset_of(black))
    found = [t for t in res if t is not None]
    print(f"highway within 200,000 steps: {len(found)}/100")
    if found:
        print(f"onset: min {min(found)}, median {statistics.median(found):.0f}, max {max(found)}")
    held = len(found) == 100 and statistics.median(found) > 10_000
    print("PREDICTION", "HELD" if held else "FAILED")
    print("never-highway starts (index):", [i for i, t in enumerate(res) if t is None][:10])
