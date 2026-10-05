"""Clock Patience: no choices, so the win chance is a property of the shuffle alone.
Predictions (journal, cycle 234): P(win) = 1/13; exact on a small deck (r ranks x s suits: 1/r); simulated on 52.
Control: a wrong rule (go to the next pile clockwise) gives a different rate - SEEN."""
import itertools, json, math, random
from fractions import Fraction
from pathlib import Path
D = Path(__file__).resolve().parent

def play(deck, r, s, wrong=False, start=None):
    # deck: list of ranks 0..r-1 (r-1 = 'king'); piles dealt in order: card i goes to pile i % r, top = last dealt
    piles = [[] for _ in range(r)]
    for i, c in enumerate(deck): piles[i % r].append(c)
    turned, cur, kings = 0, (r - 1 if start is None else start), 0
    while True:
        if not piles[cur]: return False                    # can't happen in the real rules; kept as a guard
        c = piles[cur].pop(); turned += 1
        if c == r - 1:
            kings += 1
            if kings == s: return turned == r * s
        cur = (cur + 1) % r if wrong else c

small = {}
for r, s in ((3, 2), (4, 2), (3, 3)):
    deck = [k for k in range(r) for _ in range(s)]
    perms = set(itertools.permutations(deck)); wins = sum(play(list(p), r, s) for p in perms)
    small[f"{r}x{s}"] = (wins, len(perms)); print(f"(a) exact, {r} ranks x {s} suits: {wins}/{len(perms)} = {Fraction(wins, len(perms))} (predicted 1/{r})")
a = all(Fraction(w, n) == Fraction(1, int(k.split('x')[0])) for k, (w, n) in small.items())
rng = random.Random(234); N = 400000; deck = [k for k in range(13) for _ in range(4)]; w = 0
for _ in range(N):
    rng.shuffle(deck); w += play(deck, 13, 4)
p = w / N; se = math.sqrt((1 / 13) * (12 / 13) / N); z = (p - 1 / 13) / se
print(f"(b) simulated {N:,} deals: {w:,} wins = {p:.5f} vs 1/13 = {1/13:.5f}; z = {z:+.2f}")
# cycle 234: my first control ("go to the NEXT pile clockwise") was blind: it ALSO wins about 1 in 13 (0.0754 in
# 40,000 deals), so it couldn't tell a right rule from a wrong one. Starting at pile 0 instead of the kings' pile
# does change it, to exactly 0 on every small deck (and in simulation).
wr = sum(play(rng.sample(deck, 52), 13, 4, start=0) for _ in range(40000)) / 40000
print(f"curiosity (not a control): the next-pile rule also wins about 1/13: {sum(play(rng.sample(deck, 52), 13, 4, wrong=True) for _ in range(40000)) / 40000:.4f}")
print(f"control: start at pile 0 instead of the kings' pile wins {wr:.4f} {'SEEN' if wr < 0.01 else 'NOT SEEN'}")
print("PREDICTION HELD" if a and abs(z) < 3 else "PREDICTION FAILED")
json.dump({"small": small, "sim": {"n": N, "wins": w}}, open(D / "clock.json", "w"), indent=1)
