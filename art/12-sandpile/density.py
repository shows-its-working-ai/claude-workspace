"""Cycle 139: density of the single-source sandpile = N / area, area = cells not connected to the outside through
zeros (so zeros INSIDE the pile count as pile). Sweep toppling in numpy, N = 2^10 .. 2^20."""
import numpy as np
from sandpile import sweep
def density(N):
    size = 2 * int(np.ceil(np.sqrt(N / 2))) + 9
    h, _ = sweep(N, size)
    assert h.sum() == N and h.max() < 4 and not (h[0].any() or h[-1].any() or h[:, 0].any() or h[:, -1].any())
    zero = h == 0; outside = np.zeros_like(zero); outside[0, :] = outside[-1, :] = outside[:, 0] = outside[:, -1] = True
    outside &= zero
    while True:                                        # flood fill through zeros from the border (no scipy needed)
        grow = outside.copy()
        grow[1:] |= outside[:-1]; grow[:-1] |= outside[1:]; grow[:, 1:] |= outside[:, :-1]; grow[:, :-1] |= outside[:, 1:]
        grow &= zero
        if (grow == outside).all(): break
        outside = grow
    area = int((~outside).sum())
    return area, N / area, [int((h[~outside] == v).sum()) for v in range(4)]
if __name__ == "__main__":
    rows = []
    import time
    for k in range(10, 19, 2):
        t0 = time.time()
        area, d, cnt = density(1 << k); rows.append((k, d)); el = time.time() - t0
        print(f"2^{k:2d} = {1 << k:8d} grains: area {area:8d}, density {d:.5f}, heights 0-3: {cnt} ({el:.0f} s)", flush=True)
    d16, d20 = dict(rows)[14], dict(rows)[18]
    held = 2.0 <= d20 <= 2.25 and abs(d20 - d16) < 0.01
    print(f"drift 2^14 -> 2^18: {d20 - d16:+.5f}")
    print("PREDICTION", "HELD" if held else "FAILED", "(density in [2, 2.25], drift < 0.01, 2^14 -> 2^18)")
