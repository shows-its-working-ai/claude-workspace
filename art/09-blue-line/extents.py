"""Cycle 112: count every extent on four bells.
A change = a non-empty set of disjoint adjacent swaps; on 4 bells: 12 (swap positions 1-2), 23, 34, x (12 and 34).
Here a change is named by the SWAPS it makes (not by places, as place notation does).
Extent = 24 changes from rounds, every order once, back to rounds. Counted as change sequences from rounds, so a
cycle and its reverse count twice. Also counted: those with no long places (no bell in one position for more
than 2 rows in a row, counted cyclically round the extent)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "writing"))
from ringing_15 import ring

SWAPS = {"12": [(0, 1)], "23": [(1, 2)], "34": [(2, 3)], "x": [(0, 1), (2, 3)]}
def do(row, ch):
    r = list(row)
    for a, b in SWAPS[ch]: r[a], r[b] = r[b], r[a]
    return "".join(r)

def all_extents():
    out, path, seen = [], [], {"1234"}
    def go(row):
        if len(path) == 24:
            return
        for ch in SWAPS:
            nxt = do(row, ch)
            if len(path) == 23:
                if nxt == "1234": out.append(tuple(path + [ch]))
                continue
            if nxt in seen: continue
            seen.add(nxt); path.append(ch); go(nxt); path.pop(); seen.discard(nxt)
    go("1234")
    return out

def rows_of(seq):
    rs = ["1234"]
    for ch in seq: rs.append(do(rs[-1], ch))
    return rs

def no_long_places(seq):
    rs = rows_of(seq)[:-1]                       # 24 rows, cyclic
    for bell in "1234":
        p = [r.index(bell) for r in rs]
        for i in range(24):
            if p[i] == p[(i + 1) % 24] == p[(i + 2) % 24]: return False
    return True

if __name__ == "__main__":
    ext = all_extents()
    assert all(len(set(rows_of(s)[:-1])) == 24 and rows_of(s)[-1] == "1234" for s in ext)
    # positive control: Plain Bob Minimus, as swaps. Place notation x/14/12 -> swaps x / 23 / 34.
    pn2sw = {"x": "x", "14": "23", "12": "34"}
    bob = tuple(pn2sw[c] for c in ["x", "14", "x", "14", "x", "14", "x", "12"] * 3)
    assert rows_of(bob)[1:] == ring(["x", "14", "x", "14", "x", "14", "x", "12"], 3), "swap translation wrong"
    good = [s for s in ext if no_long_places(s)]
    rev = lambda s: tuple(reversed(s))
    print(f"extents from rounds (direction counted): {len(ext)}")
    print(f"  as undirected cycles through rounds: {len({min(s, rev(s)) for s in ext})}")
    print(f"with no long places: {len(good)}")
    print("Plain Bob Minimus found:", bob in ext, "| has no long places:", bob in good)
    # up to where you start, which way round, and mirror image (bells counted from the back): how many really differ?
    mir = {"12": "34", "34": "12", "23": "23", "x": "x"}
    def canon(s):
        c = []
        for t in (s, rev(s)):
            for u in (t, tuple(mir[x] for x in t)):
                c += [u[k:] + u[:k] for k in range(24)]
        return min(c)
    classes = sorted({" ".join(canon(s)[:8]) for s in good})
    print(f"no-long-places extents, essentially different: {len(classes)}: {classes}")
    print("all of them repeat an 8-change lead:", all(s[i] == s[i % 8] for s in good for i in range(24)))
    held = 100 <= len(ext) <= 10000 and len(good) * 10 <= len(ext)
    print("PREDICTION", "HELD" if held else "FAILED", "(100..10,000 extents; no-long-places cuts >= 10x)")
