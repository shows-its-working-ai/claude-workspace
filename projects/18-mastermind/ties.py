"""Tie-breaks in Knuth's Mastermind strategy (cycle 167). Same minimax rule, three ways to pick among equally good
guesses. The page quotes these three results."""
from collections import Counter
from pathlib import Path
src = (Path(__file__).resolve().parent / "knuth.py").read_text(encoding="utf-8")
exec(src.split("memo = {}")[0])                 # CODES, FB, IDX, score: the same tables knuth.py builds
def run(keyf, first="1122"):
    memo = {}
    def best(c):
        if len(c) == 1: return c[0]
        cs = set(c); return min(CODES, key=lambda g: keyf(g, c, cs))
    tot = mx = 0
    for s in CODES:
        cands, n, g = CODES, 0, first
        while True:
            n += 1
            if g == s: break
            f = FB[IDX[g]][IDX[s]]; cands = tuple(x for x in cands if FB[IDX[g]][IDX[x]] == f)
            if cands not in memo: memo[cands] = best(list(cands))
            g = memo[cands]
        tot += n; mx = max(mx, n)
    return tot, mx
def worst(g, c): return max(Counter(FB[IDX[g]][IDX[s]] for s in c).values())
V = {
    "lowest-numbered (the page)": lambda g, c, cs: (worst(g, c), g not in cs, g),
    "highest-numbered": lambda g, c, cs: (worst(g, c), g not in cs, [-int(ch) for ch in g]),
    "no preference for possible codes": lambda g, c, cs: (worst(g, c), g),
}
for k, f in V.items():
    tot, mx = run(f); print(f"{k}: total {tot}, average {tot / 1296:.4f}, worst {mx}")
