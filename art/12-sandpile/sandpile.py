"""Cycle 138: abelian sandpile, N grains poured on the centre of an unbounded grid (grid grows as needed).
Two independent toppling orders (sweep vs random queue) must give identical final heights and identical per-square
topple counts. Also: grains conserved (none lost: unbounded grid), final heights all < 4, D4 symmetry."""
import json, random, sys
from pathlib import Path
import numpy as np
def sweep(N, size):
    h = np.zeros((size, size), np.int64); c = size // 2; h[c, c] = N; top = np.zeros_like(h)
    while True:
        k = h // 4
        if not k.any(): return h, top
        top += k; h -= 4 * k
        h[1:, :] += k[:-1, :]; h[:-1, :] += k[1:, :]; h[:, 1:] += k[:, :-1]; h[:, :-1] += k[:, 1:]
def queue(N, size, seed=1):
    rng = random.Random(seed); h = [[0] * size for _ in range(size)]; top = [[0] * size for _ in range(size)]
    c = size // 2; h[c][c] = N; todo = [(c, c)]
    while todo:
        i = rng.randrange(len(todo)); todo[i], todo[-1] = todo[-1], todo[i]; r, s = todo.pop()
        if h[r][s] < 4: continue
        k = h[r][s] // 4; h[r][s] -= 4 * k; top[r][s] += k
        for a, b in ((r + 1, s), (r - 1, s), (r, s + 1), (r, s - 1)):
            h[a][b] += k
            if h[a][b] >= 4: todo.append((a, b))
        if h[r][s] >= 4: todo.append((r, s))
    return np.array(h), np.array(top)
if __name__ == "__main__":
    N, size = 1 << 12, 81
    h1, t1 = sweep(N, size); h2, t2 = queue(N, size)
    edge_clear = h1[0].sum() + h1[-1].sum() + h1[:, 0].sum() + h1[:, -1].sum() == 0
    same = (h1 == h2).all() and (t1 == t2).all()
    d4 = all((h1 == g).all() for g in (np.rot90(h1), np.rot90(h1, 2), np.rot90(h1, 3), h1.T, h1[::-1], h1[:, ::-1]))
    print(f"N={N}: grains kept {int(h1.sum())}, max height {int(h1.max())}, edge clear {edge_clear}")
    print(f"sweep == random order (heights AND topple counts): {same}; total topples {int(t1.sum())}")
    print(f"all 8 symmetries of the square: {d4}")
    print("PREDICTION", "HELD" if same and d4 and h1.sum() == N and h1.max() < 4 and edge_clear else "FAILED")
    (Path(__file__).resolve().parent / "sandpile4096.json").write_text(json.dumps(h1.tolist()), encoding="utf-8")
