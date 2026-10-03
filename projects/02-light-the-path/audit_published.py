"""Cycle 65: audit ALL my gliders against published phase strings (arXiv 0706.3348 appendix + Table 2), because
cycle 64 showed speed alone can misname a glider. C in particular has three variants (C1, C2, C3), all speed 0.
Prediction (written first): A, B and G each match only their own published strings; my C is C1 (the smallest
and, I guess, the most common), and nothing else matches more than one type.
Strings that also occur in PURE ether (at any phase) are useless as evidence and are dropped first.
Also checked: my measured (period, shift) against Table 2's period/shift, not just the speed."""
import numpy as np
TILE = np.array([int(c) for c in "00010011011111"], dtype=np.uint8)
TABLE = np.array([(110 >> i) & 1 for i in range(8)], dtype=np.uint8)
step = lambda r: TABLE[4 * np.roll(r, 1) + 2 * r + np.roll(r, -1)]
NT = 40; W = 14 * NT; base = np.tile(TILE, NT); OFF = 14 * 20
PUB = {   # (period, shift) from Table 2's speed written as d/p, and f1_1 phase strings from the appendix
    "A":  ((3, 2),    ["111110", "11111000111000100110", "11111000100110100110"]),
    "B":  ((4, -2),   ["11111010", "11111000", "1111100010011000100110", "11100110"]),
    "C1": ((7, 0),    ["111110000"]),
    "C2": ((7, 0),    ["11111000000100110"]),
    "C3": ((7, 0),    ["11111011010"]),
    "Ebar": ((30, -8), ["111110000100011111010", "111110001000110011000", "11111000100110011101110011000100110",
                        "111011011101011100110", "111110111111011111010", "111110001110000111000",
                        "11111000100110100011010011000100110", "111110011111011100110", "111110001011000111010",
                        "111110001001111100110", "11111000100110110001011111000100110", "111111001111000100110"]),
    "E":  ((15, -4),  ["1111100000000100110", "1111100010000000110", "1111100010011000000", "1110000011000100110",
                       "1111101000011100110", "1111100011100011010", "1111101100000100110", "1111100011110000110",
                       "1111100010011001000", "1110110011000100110", "1111101111011100110", "1111100011100111010",
                       "1111100010011010110", "1111111111000100110"]),
    "G":  ((42, -14), ["111110100111110011100110"]),
}
MINE = {"A": [0, 5], "B": [7, 14], "C": [6, 23], "Ebar": [6], "G": [2, 18]}   # seeds from glider_search3

def texts(row, phases=84):                                       # 84 = lcm-friendly: covers periods 3,4,7,42
    out = []
    for _ in range(phases):
        s = "".join(map(str, row)); out.append(s + s[:60]); row = step(row)
    return out
ether_texts = texts(base.copy())
useless = {s for _, ss in PUB.values() for s in ss if any(s in t for t in ether_texts)}
print("strings that occur in pure ether (dropped):", sorted(useless, key=len))
pub = {k: (pd, [s for s in ss if s not in useless]) for k, (pd, ss) in PUB.items()}

def measure(seed, T=400):
    row = base.copy(); row[[OFF + o for o in seed]] ^= 1; clean = base.copy(); hist = []
    for _ in range(T): row, clean = step(row), step(clean)
    settled = row.copy()
    for _ in range(3 * 60 + 1): hist.append(row != clean); row, clean = step(row), step(clean)
    for p in range(1, 61):
        for d in range(-30, 31):
            if all(np.array_equal(np.roll(hist[r * p], d), hist[(r + 1) * p]) for r in range(3)): return (p, d), settled
    return None, settled
for name, seed in MINE.items():
    pd, row = measure(seed)
    ts = texts(row)
    hits = {k: sum(any(s in t for t in ts) for s in ss) for k, (_, ss) in pub.items() if ss}
    tot = {k: len(ss) for k, (_, ss) in pub.items() if ss}
    matched = [k for k, h in hits.items() if h]
    period_ok = [k for k, (p2, _) in pub.items() if p2 == pd]
    print(f"my {name:5s} (period, shift) = {pd}; Table 2 types with that exact (p, d): {period_ok}; "
          f"string hits: " + ", ".join(f"{k} {hits[k]}/{tot[k]}" for k in matched))

# --- step 2: specificity. A string that shows up around several DIFFERENT gliders of mine is a generic local
# pattern, not evidence. Keep only strings that occur around exactly one of my gliders.
where = {}
for name, seed in MINE.items():
    ts = texts(measure(seed)[1])
    for k, (_, ss) in pub.items():
        for s in ss:
            if any(s in t for t in ts): where.setdefault((k, s), set()).add(name)
print()
for (k, s), names in sorted(where.items()):
    tag = "SPECIFIC" if len(names) == 1 else "generic "
    print(f"  {tag} {k:5s} {s:36s} found around my {sorted(names)}")

# --- step 3: C variants by direct simulation. Embed each published C string in ether (open row), let it run,
# take the stationary core (40 cells around where it was placed) at 7 consecutive steps, and look for that exact
# 7-step movie in my C's raw rows (any position, any phase).
def open_step(r):
    p = np.r_[0, r, 0]; return TABLE[4 * p[:-2] + 2 * p[1:-1] + p[2:]]
ETH = np.array([int(c) for c in "11111000100110"], dtype=np.uint8)
def core_movie(s, PAD=40, T=140, half=20):
    e = np.array([int(c) for c in s], dtype=np.uint8); row = np.r_[np.tile(ETH, PAD), e, np.tile(ETH, PAD)]
    mid = 14 * PAD + len(e) // 2
    for _ in range(T): row = open_step(row)
    frames = []
    for _ in range(7): frames.append("".join(map(str, row[mid - half: mid + half]))); row = open_step(row)
    return frames
myC = measure(MINE["C"])[1]; mine_frames = texts(myC, phases=14)
for k in ("C1", "C2", "C3"):
    mv = core_movie(PUB[k][1][0])
    found = any(all(mv[i] in mine_frames[ph + i] for i in range(7)) for ph in range(7))
    # positional consistency: the 7 frames must line up at the SAME offset in my rows
    same_pos = any(len({mine_frames[ph + i].find(mv[i]) for i in range(7)} - {-1}) == 1 and all(mv[i] in mine_frames[ph + i] for i in range(7)) for ph in range(7))
    print(f"published {k} simulated: its 7-step core movie {'APPEARS' if same_pos else 'does NOT appear'} in my C")

# --- step 3b (the window above included shifted ether, so it proves nothing): search the other way. Take MY C's
# core = its defect cells + 3 on each side, over 7 consecutive steps, and look for that 7-step movie, at one
# consistent offset, inside each published C's simulated row. Control: my own C row must find itself.
def my_core_movie(seed):
    row = base.copy(); row[[OFF + o for o in seed]] ^= 1; clean = base.copy()
    for _ in range(400): row, clean = step(row), step(clean)
    x = np.nonzero(row != clean)[0]; a, b = int(x.min()) - 3, int(x.max()) + 4
    mv = []
    for _ in range(7): mv.append("".join(map(str, row[a:b]))); row, clean = step(row), step(clean)
    return mv, b - a
def contains_movie(rows7, mv):
    for ph in range(7):
        offs = None
        for i in range(7):
            r = rows7[ph + i]; o = {j for j in range(len(r) - len(mv[i]) + 1) if r.startswith(mv[i], j)}
            offs = o if offs is None else offs & o
            if not offs: break
        if offs: return True
    return False
def published_rows(s, PAD=40, T=140, n=14):
    e = np.array([int(c) for c in s], dtype=np.uint8); row = np.r_[np.tile(ETH, PAD), e, np.tile(ETH, PAD)]
    for _ in range(T): row = open_step(row)
    out = []
    for _ in range(n): out.append("".join(map(str, row[200:-200]))); row = open_step(row)
    return out
mv, w = my_core_movie(MINE["C"])
print(f"\nmy C core: {w} cells wide; frame 0 = {mv[0]}")
own = [("".join(map(str, r))) for r in []]
myrows = texts(measure(MINE["C"])[1], phases=14)
print("CONTROL my C finds itself:", contains_movie(myrows, mv))
for k in ("C1", "C2", "C3"):
    print(f"my C's 7-step core appears in simulated published {k}:", contains_movie(published_rows(PUB[k][1][0]), mv))

# --- step 4: the other direction. My C's defect is ~44 cells wide; published C variants are 9-23. Is my "C" a
# COMPOUND of published Cs? Take each published C's own core (its string's cells +-3 after it settles, stationary)
# as a 7-step movie and look for it inside my C's rows. Then count how many times / where.
def published_core_movie(s, PAD=40, T=140, pad=3):
    e = np.array([int(c) for c in s], dtype=np.uint8); row = np.r_[np.tile(ETH, PAD), e, np.tile(ETH, PAD)]
    a, b = 14 * PAD - pad, 14 * PAD + len(e) + pad
    for _ in range(T): row = open_step(row)
    mv = []
    for _ in range(7): mv.append("".join(map(str, row[a:b]))); row = open_step(row)
    return mv
def find_all(rows7, mv):
    hits = set()
    for ph in range(7):
        offs = None
        for i in range(7):
            r = rows7[ph + i]; o = {j for j in range(len(r) - len(mv[i]) + 1) if r.startswith(mv[i], j)}
            offs = o if offs is None else offs & o
            if not offs: break
        if offs: hits |= {(ph, j) for j in offs}
    return hits
xC = np.nonzero(measure(MINE["C"])[1] != np.tile(TILE, NT))[0]   # rough location only (phase differs), for context
for k in ("C1", "C2", "C3"):
    h = find_all(myrows, published_core_movie(PUB[k][1][0]))
    print(f"published {k}'s core movie found inside my C at (phase, offset): {sorted(h)[:6]}{' ...' if len(h) > 6 else ''}")
    hether = find_all(texts(base.copy(), phases=14), published_core_movie(PUB[k][1][0]))
    print(f"   control: found in PURE ether: {bool(hether)}")

# --- step 5: same idea for MOVING gliders. Simulate each published string, take its core window at 3 times one
# period apart (the window moves by the catalogue shift d each period), and require my glider's rows to contain
# those 3 frames at offsets j, j+d, j+2d. E-bar is the positive control (already identified by 9 strings).
def published_core_frames(s, p, d, PAD=60, T=210, pad=3):
    e = np.array([int(c) for c in s], dtype=np.uint8); row = np.r_[np.tile(ETH, PAD), e, np.tile(ETH, PAD)]
    a0, b0 = 14 * PAD - pad, 14 * PAD + len(e) + pad
    sh = d * (T // p)                                             # where the core has moved to by step T (T multiple of p)
    for _ in range(T): row = open_step(row)
    frames = []
    for r in range(3):
        a, b = a0 + sh + r * d, b0 + sh + r * d
        frames.append("".join(map(str, row[a:b])))
        for _ in range(p): row = open_step(row)
    return frames
def my_rows(seed, n):
    row = base.copy(); row[[OFF + o for o in seed]] ^= 1
    for _ in range(400): row = step(row)
    out = []
    for _ in range(n): s = "".join(map(str, row)); out.append(s + s[:80]); row = step(row)
    return out
for k, mine in (("A", "A"), ("B", "B"), ("G", "G"), ("Ebar", "Ebar"), ("E", "Ebar")):
    (p, d), strs = PUB[k]
    rows = my_rows(MINE[mine], 3 * p + 84)
    best = 0
    for s in strs:
        if s in useless: continue
        fr = published_core_frames(s, p, d, T=p * (210 // p))
        ok = any(any(rows[ph].startswith(fr[0], j) and rows[ph + p].startswith(fr[1], (j + d) % W) and
                     rows[ph + 2 * p].startswith(fr[2], (j + 2 * d) % W) for j in range(W)) for ph in range(84))
        best += ok
    print(f"published {k:4s} simulated, tracked over 3 periods: matches my {mine} for {best}/{len([s for s in strs if s not in useless])} strings")
