"""Knuth's minimax Mastermind strategy, from scratch (cycle 165). Writes knuth.json: code -> number of guesses."""
import json
from collections import Counter
from itertools import product
from pathlib import Path
CODES = ["".join(c) for c in product("123456", repeat=4)]
def score(g, s):
    black = sum(a == b for a, b in zip(g, s))
    white = sum(min(g.count(c), s.count(c)) for c in "123456") - black
    return black, white
IDX = {c: i for i, c in enumerate(CODES)}
FB = [[score(g, s) for s in CODES] for g in CODES]
def best(cands):
    if len(cands) == 1: return cands[0]
    cs = set(cands); top = None
    for g in CODES:
        worst = max(Counter(FB[IDX[g]][IDX[s]] for s in cands).values())
        key = (worst, g not in cs, g)
        if top is None or key < top: top = key
    return top[2]
memo = {}
def solve(secret):
    cands, n, guess = CODES, 0, "1122"
    while True:
        n += 1
        if guess == secret: return n
        f = FB[IDX[guess]][IDX[secret]]
        cands = tuple(s for s in cands if FB[IDX[guess]][IDX[s]] == f)
        if cands not in memo: memo[cands] = best(list(cands))
        guess = memo[cands]
res = {s: solve(s) for s in CODES}
hist = Counter(res.values())
(Path(__file__).resolve().parent / "knuth.json").write_text(json.dumps(res), encoding="utf-8")
print("first guess 1122; guesses needed:", dict(sorted(hist.items())))
print(f"max {max(res.values())}, average {sum(res.values()) / len(res):.4f} ({sum(res.values())}/{len(res)})")
print("PREDICTION HELD" if max(res.values()) <= 5 else "PREDICTION FAILED")
