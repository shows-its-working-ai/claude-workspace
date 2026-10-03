"""Control for collide.py's classifier: each known glider ALONE, through the same pipeline, must be named correctly."""
import numpy as np
import collide as C          # re-uses its constants/functions (importing re-runs the search; that's fine, ~2 s)
rows = np.repeat(C.base[None, :], 5, axis=0); names = list(C.SEEDS)
for i, n in enumerate(names): rows[i, [C.L0 + o for o in C.SEEDS[n]]] ^= 1
clean = C.base.copy(); hist = []
for t in range(C.T + 1):
    if t > C.T - C.REPS * C.PMAX - 1: hist.append(rows != clean)
    rows = C.step(rows); clean = C.step(clean)
C.hist = np.stack(hist, axis=1)
ok = True
for i, n in enumerate(names):
    cells = np.nonzero(C.hist[i, -1])[0]; cls = C.clusters(cells)
    got = [C.CAT.get(C.identify(i, cl), "?") for cl in cls]
    print(f"{n} alone -> clusters {len(cls)}, identified {got}"); ok &= got == [n]
print("CONTROL OK" if ok else "CONTROL FAILED")
