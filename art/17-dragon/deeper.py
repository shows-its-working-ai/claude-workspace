"""Does 'no corner touched three times' survive to 22 folds? (cycle 171). Creases by the bit rule, which dragon.py
showed equals the fold recurrence up to 16; above 16 the bit rule is all we use."""
import numpy as np
def run(n, all_left=False):
    k = np.arange(1, 2 ** n, dtype=np.int64)
    left = (k & ((k & -k) << 1)) == 0
    if all_left: left[:] = True                                             # control: circles one square forever
    turn = np.where(left, 1, 3).astype(np.int64)                         # L = +1 quarter turn, R = -1 (= +3)
    d = np.concatenate([[0], np.cumsum(turn) % 4])                          # direction of each of the 2^n edges
    dx = np.array([1, 0, -1, 0])[d]; dy = np.array([0, 1, 0, -1])[d]
    x = np.concatenate([[0], np.cumsum(dx)]); y = np.concatenate([[0], np.cumsum(dy)])
    key = (x.astype(np.int64) << 32) + (y.astype(np.int64) & 0xffffffff)
    _, counts = np.unique(key, return_counts=True)
    a = np.minimum(np.stack([x[:-1] * 2 + dx, y[:-1] * 2 + dy]), 10 ** 9)   # edge midpoints, doubled: unique per edge
    ekey = (a[0].astype(np.int64) << 32) + (a[1].astype(np.int64) & 0xffffffff)
    reused = len(ekey) - len(np.unique(ekey))
    return len(counts), int((counts == 2).sum()), int((counts > 2).sum()), reused
c = run(16); print("control, n=16 vs dragon.py (36982 corners, 28555 twice, 0, 0):", c, "AGREE" if c == (36982, 28555, 0, 0) else "DISAGREE")
c = run(6, all_left=True); print("control, all-left path (must show >2 corners and reused edges):", c, "SEEN" if c[2] > 0 and c[3] > 0 else "BLIND")
for n in range(17, 23):
    co, tw, mo, re = run(n)
    print(f"n={n}: {2**n} edges, {co} corners, twice {tw} ({tw / co:.4f}), more than twice {mo}, edges reused {re}")
