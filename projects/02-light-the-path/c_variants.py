"""Cycle 66: find seeds for a LONE C1 and a LONE C3 (my "C" turned out to be a C3+C1 pair, cycle 65).
Prediction (written first): among all 1-3 flips in a two-tile (28-cell) window, some seed gives a lone C1 and some
gives a lone C3 (stationary, period 7, defect no wider than the catalogue's 23), and none gives C2.
Identification uses the published cores (arXiv 0706.3348, simulated in ether), as in audit_published.py:
the 7-step core movie must appear at ONE consistent offset in the candidate's rows. Controls: the published
cores never appear in pure ether, and my old two-flip "C" seed must come out as containing BOTH C1 and C3."""
import itertools
import numpy as np
TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
step = lambda r: TABLE[4 * np.roll(r, 1, axis=-1) + 2 * r + np.roll(r, -1, axis=-1)]
NT = 40; W = 14 * NT; base = np.tile(TILE, NT); OFF = 14 * 20
ETH = np.array([int(c) for c in "11111000100110"], dtype=np.uint8)
PUBC = {   # all variants/phases from the appendix (cycle 66 fetch); identification = ANY of them matches
    "C1": ["111110000", "11111000100011000100110", "11111000100110011100110", "111011010",
           "11111011111111000100110", "11111000111000000100110", "11111000100110100000110"],
    "C2": ["11111000000100110", "11111000100000110", "11111000100110000", "11100011000100110",
           "11111010011100110", "11111000111011010", "1111100010011011111111000100110"],
    "C3": ["11111011010", "1111100011111111000100110", "1111100010011000000100110", "11100000110",
           "11111010000", "1111100011100011000100110", "1111100010011010011100110"]}

def open_step(r):
    p = np.r_[0, r, 0]; return TABLE[4 * p[:-2] + 2 * p[1:-1] + p[2:]]
def published_core_movie(s, PAD=40, T=140, pad=3):
    e = np.array([int(c) for c in s], dtype=np.uint8); row = np.r_[np.tile(ETH, PAD), e, np.tile(ETH, PAD)]
    a, b = 14 * PAD - pad, 14 * PAD + len(e) + pad
    for _ in range(T): row = open_step(row)
    mv = []
    for _ in range(7): mv.append("".join(map(str, row[a:b]))); row = open_step(row)
    return mv
MOVIES = {k: [published_core_movie(x) for x in ss] for k, ss in PUBC.items()}
def contains(rows14, mv):
    for ph in range(7):
        offs = None
        for i in range(7):
            r = rows14[ph + i]; o = {j for j in range(len(r) - len(mv[i]) + 1) if r.startswith(mv[i], j)}
            offs = o if offs is None else offs & o
            if not offs: break
        if offs: return True
    return False
def rows_of(row, n=14):
    out = []
    for _ in range(n): s = "".join(map(str, row)); out.append(s + s[:60]); row = step(row)
    return out
def ident(row):
    rs = rows_of(row); return sorted(k for k, mvs in MOVIES.items() if any(contains(rs, mv) for mv in mvs))

ctrl_ether = ident(base.copy())
old = base.copy(); old[[OFF + 6, OFF + 23]] ^= 1
for _ in range(400): old = step(old)
print("CONTROL pure ether ->", ctrl_ether or "nothing", "| CONTROL old 'C' seed [6, 23] ->", ident(old))

seeds = [c for n in (1, 2, 3) for c in itertools.combinations(range(28), n)]
rows = np.repeat(base[None, :], len(seeds), axis=0)
for i, sd in enumerate(seeds): rows[i, [OFF + o for o in sd]] ^= 1
clean = base.copy()
for _ in range(400): rows, clean = step(rows), step(clean)
hist = [];
r2, c2 = rows.copy(), clean.copy()
for _ in range(22): hist.append(r2 != c2); r2, c2 = step(r2), step(c2)
hist = np.stack(hist, axis=1)                                     # seeds x 22 x W
stationary = np.all([np.array_equal(hist[i, 0], hist[i, 7]) and np.array_equal(hist[i, 7], hist[i, 14]) and
                     np.array_equal(hist[i, 14], hist[i, 21]) and hist[i, 0].any() for i in range(len(seeds))], axis=0) \
    if False else np.array([np.array_equal(hist[i, 0], hist[i, 7]) and np.array_equal(hist[i, 7], hist[i, 14])
                            and np.array_equal(hist[i, 14], hist[i, 21]) and hist[i, 0].any() for i in range(len(seeds))])
cand = np.nonzero(stationary)[0]
print(f"{len(seeds)} seeds; {len(cand)} end as a stationary period-7 defect")
found = {}
for i in cand:
    x = np.nonzero(hist[i, 0])[0]; width = int(x.max() - x.min() + 1)
    ids = ident(rows[i]); key = "+".join(ids) or "unmatched"
    found.setdefault(key, []).append((seeds[i], width))
for key, lst in sorted(found.items(), key=lambda kv: -len(kv[1])):
    smallest = min(lst, key=lambda t: (len(t[0]), t[1]))
    print(f"  {key:10s} {len(lst):4d} seeds; widths {sorted({w for _, w in lst})[:8]}; simplest seed {smallest[0]} (width {smallest[1]})")

# the seeds the gliders page shows must identify as exactly one variant each
def ident_seed(sd):
    r = base.copy(); r[[OFF + o for o in sd]] ^= 1
    for _ in range(400): r = step(r)
    return ident(r)
page = {"C2": (3, 9, 13), "C3": (12, 14, 18)}
res = {k: ident_seed(sd) for k, sd in page.items()}
print("page seeds identify as:", res)
print("C VARIANTS OK" if all(res[k] == [k] for k in page) and not ctrl_ether and ident(old) == ["C1", "C3"] else "C VARIANTS FAILED")
