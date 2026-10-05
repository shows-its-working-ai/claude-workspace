"""Push Your Luck (solo Pig): exact expectations. Predictions (journal, cycle 247): (a) hold-at-20 maximises expected
points per turn (~8.14), 21 might tie; (b) GUESS hold-at-20 needs 11-13 turns on average to reach 100; (c) GUESS the
optimal turn-minimising strategy saves under one turn. Control: hold-at-2 is much worse - SEEN."""
import json, random
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
D = Path(__file__).resolve().parent
GOAL = 100

def turn_points(k):                      # expected banked points in one turn, holding at turn total >= k (exact)
    @lru_cache(maxsize=None)
    def E(t):
        if t >= k: return F(t)
        return sum(E(t + r) for r in range(2, 7)) / 6        # a 1 banks nothing
    return E(0)
pts = {k: turn_points(k) for k in range(1, 41)}
best = max(pts, key=lambda k: pts[k]); ties = [k for k in pts if pts[k] == pts[best]]
print(f"(a) best threshold(s) for points per turn: {ties}; value {float(pts[best]):.4f}; at 20: {float(pts[20]):.4f}, 21: {float(pts[21]):.4f}")

def turns_hold(k):                       # expected turns to reach GOAL, holding at min(k, needed)
    # value iteration over score s: T(s) = 1 + E[T(s')] where s' = s + banked; solve by iterating to convergence
    T = [0.0] * (GOAL + 1)
    for _ in range(4000):
        new = [0.0] * (GOAL + 1)
        for s in range(GOAL - 1, -1, -1):
            need = min(k, GOAL - s)
            @lru_cache(maxsize=None)
            def V(t):                    # expected FUTURE turns after this one, from turn total t
                if t >= need: return T[min(GOAL, s + t)]
                return (T[s] + sum(V(t + r) for r in range(2, 7))) / 6
            new[s] = 1 + V(0)
        if max(abs(a - b) for a, b in zip(new, T)) < 1e-12: break
        T = new
    return T[0]
t20 = turns_hold(20); t2 = turns_hold(2)
print(f"(b) hold-at-20: expected turns to {GOAL} = {t20:.4f}")
print(f"control: hold-at-2 expected turns = {t2:.2f} {'SEEN' if t2 > t20 + 3 else 'NOT SEEN'}")

def optimal():                           # minimise expected turns: at each (s, t) choose roll or hold
    T = [0.0] * (GOAL + 1)
    for _ in range(4000):
        new = [0.0] * (GOAL + 1); policy = {}
        for s in range(GOAL - 1, -1, -1):
            @lru_cache(maxsize=None)
            def V(t):
                if s + t >= GOAL: return 0.0
                roll = (T[s] + sum(V(t + r) for r in range(2, 7))) / 6
                hold = T[s + t] if t > 0 else float("inf")
                return min(roll, hold)
            new[s] = 1 + V(0)
        if max(abs(a - b) for a, b in zip(new, T)) < 1e-12: break
        T = new
    return T[0]
topt = optimal()
print(f"(c) optimal strategy: expected turns = {topt:.4f}; saving over hold-at-20 = {t20 - topt:.4f}")
rng = random.Random(247); N = 200000; tot = 0
for _ in range(N):
    s = n = 0
    while s < GOAL:
        n += 1; t = 0
        while t < min(20, GOAL - s):
            r = rng.randint(1, 6)
            if r == 1: t = 0; break
            t += r
        s += t
    tot += n
print(f"simulated hold-at-20, {N:,} games: {tot / N:.4f} turns (exact {t20:.4f})")
a = 20 in ties and 8.0 < float(pts[20]) < 8.3; b = 11 <= t20 <= 13; c = 0 < t20 - topt < 1 and abs(tot / N - t20) < 0.05
print("PREDICTION HELD" if a and b and c else "PREDICTION FAILED")
json.dump({"pts20": float(pts[20]), "best_thresholds": ties, "turns20": t20, "turns_opt": topt}, open(D / "pig.json", "w"), indent=1)
