"""Cycle 135: count directed open knight's tours on n x n boards by depth-first search (no shortcuts), plus how many
start from each square of 5x5. Prediction: 0 for n = 2, 3, 4 and 1728 for n = 5."""
import json, sys
from pathlib import Path
MOVES = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
def count(n):
    nbr = [[(r + dr) * n + c + dc for dr, dc in MOVES if 0 <= r + dr < n and 0 <= c + dc < n] for r in range(n) for c in range(n)]
    total = n * n; per = [0] * total; seen = [False] * total
    def go(v, depth):
        if depth == total: return 1
        s = 0
        for w in nbr[v]:
            if not seen[w]: seen[w] = True; s += go(w, depth + 1); seen[w] = False
        return s
    for v in range(total):
        seen[v] = True; per[v] = go(v, 1); seen[v] = False
    return sum(per), per
if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    res = {}
    for n in (1, 2, 3, 4, 5):
        tot, per = count(n); res[n] = {"total": tot, "per_start": per}
        print(f"{n}x{n}: {tot} directed open tours")
    print("5x5 tours starting at each square:"); per = res[5]["per_start"]
    for r in range(5): print("   " + " ".join(f"{per[r * 5 + c]:4d}" for c in range(5)))
    held = res[5]["total"] == 1728 and all(res[n]["total"] == 0 for n in (2, 3, 4))
    print("PREDICTION", "HELD" if held else "FAILED", "(1728 on 5x5; none on 2x2..4x4)")
    (Path(__file__).resolve().parent / "tours.json").write_text(json.dumps({str(k): v for k, v in res.items()}), encoding="utf-8")
