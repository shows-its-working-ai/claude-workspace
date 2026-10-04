"""Dragon curve from simulated paper folding (cycle 169). Writes dragon.json: n -> crease string (L/R), n <= 16."""
import json
from pathlib import Path
def fold(n):                       # creases of a strip folded n times, read along the strip after unfolding
    s = ""
    for _ in range(n):             # folding once more: old creases, a new middle crease, then the old ones mirrored
        s = s + "L" + "".join("R" if c == "L" else "L" for c in reversed(s))
    return s
def rule(k): return "L" if (k & (((k & -k) << 1))) == 0 else "R"
bad, out = [], {}
for n in range(1, 17):
    s = fold(n); out[n] = s
    if s != "".join(rule(k) for k in range(1, 2 ** n)): bad.append((n, "rule"))
    x, y, dx, dy = 0, 0, 1, 0; edges, verts = set(), {(0, 0): 1}
    for c in s + "E":
        e = frozenset({(x, y), (x + dx, y + dy)})
        if e in edges: bad.append((n, "edge reused")); break
        edges.add(e); x, y = x + dx, y + dy; verts[(x, y)] = verts.get((x, y), 0) + 1
        if c == "L": dx, dy = -dy, dx
        elif c == "R": dx, dy = dy, -dx
    twice = sum(v == 2 for v in verts.values()); more = sum(v > 2 for v in verts.values())
    if n in (4, 5, 8, 12, 16): print(f"n={n}: {2**n} edges, {len(verts)} corners, {twice} visited twice, {more} more than twice")
(Path(__file__).resolve().parent / "dragon.json").write_text(json.dumps(out), encoding="utf-8")
print(f"n checked: 16; failures: {len(bad)}", bad[:5])
print("PREDICTION HELD" if not bad else "PREDICTION FAILED")
