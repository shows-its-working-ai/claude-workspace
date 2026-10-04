"""Smith-style Truchet tilings (cycle 188). Tile type 0: arcs cap the top-left and bottom-right corners; type 1: the
top-right and bottom-left. Each tile corner is a piece of some region; union-find joins pieces that touch without an
arc between them, then checks 2-colourability of the arc-adjacency graph and the parity claim."""
import random
def regions(t, R, C, wrong=False):
    par = {}
    def f(x):
        while par.setdefault(x, x) != x: par[x] = par[par[x]]; x = par[x]
        return x
    def u(a, b): par[f(a)] = f(b)
    TL, TR, BR, BL = range(4)
    for r in range(R):
        for c in range(C):
            if wrong: u((r, c, TL), (r, c, TR))                  # control: join two NEIGHBOURING corners (opposite parity)
            elif t[r][c] == 0: u((r, c, TR), (r, c, BL))         # middle band joins the two uncapped corners
            else: u((r, c, TL), (r, c, BR))
            if c + 1 < C: u((r, c, TR), (r, c + 1, TL)); u((r, c, BR), (r, c + 1, BL))   # across a tile edge: no arc
            if r + 1 < R: u((r, c, BL), (r + 1, c, TL)); u((r, c, BR), (r + 1, c, TR))
    seps = []                                                    # pairs of pieces separated by an arc
    for r in range(R):
        for c in range(C):
            caps = (TL, BR) if t[r][c] == 0 else (TR, BL)
            mid = TR if t[r][c] == 0 else TL
            for k in caps: seps.append((f((r, c, k)), f((r, c, mid))))
    return f, seps
def vertex(r, c, k): return (r + (k in (2, 3)), c + (k in (1, 2)))       # grid point under tile corner k
rng = random.Random(188); bad = 0; nreg = []
for trial in range(1000):
    R = C = 12; t = [[rng.randint(0, 1) for _ in range(C)] for _ in range(R)]
    f, seps = regions(t, R, C)
    parity = {}
    for r in range(R):
        for c in range(C):
            for k in range(4):
                y, x = vertex(r, c, k); p = (y + x) % 2; g = f((r, c, k))
                if parity.setdefault(g, p) != p: bad += 1                 # a region with both parities
    if any(parity[a] == parity[b] for a, b in seps): bad += 1            # two arc-neighbours the same colour
    nreg.append(len(parity))
print(f"1000 random 12x12 tilings: failures {bad}; regions per tiling {min(nreg)}..{max(nreg)}")
cb = 0                                                           # control: a mis-modelled tile must be caught
for trial in range(20):
    t = [[rng.randint(0, 1) for _ in range(12)] for _ in range(12)]; f, _ = regions(t, 12, 12, wrong=True); par = {}
    for r in range(12):
        for c in range(12):
            for k in range(4):
                y, x = vertex(r, c, k); p = (y + x) % 2
                if par.setdefault(f((r, c, k)), p) != p: cb += 1
print(f"control (wrong corners joined): parity violations {cb}", "SEEN" if cb else "BLIND")
print("PREDICTION HELD" if bad == 0 and cb else "PREDICTION FAILED")
