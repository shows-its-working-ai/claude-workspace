"""Cycle 147: weaving drawdowns. cell(r, c) = warp on top iff tieup[treadle[r]] contains threading[c].
Colour shown = warp colour if warp on top, else weft colour. Drafts: plain weave, 2/2 twill, houndstooth,
chevron. Checks: plain weave is a checkerboard; every cell of a balanced 2/2 twill has exactly 2 of 4 shafts
up per row; houndstooth colour pattern has period 8 in both directions; chevron mirrors at its reversal."""
import json
from pathlib import Path
def drawdown(threading, tieup, treadling, rows, cols):
    return [[1 if threading[c % len(threading)] in tieup[treadling[r % len(treadling)]] else 0 for c in range(cols)] for r in range(rows)]
def colours(dd, warp_col, weft_col):
    return [[warp_col[c % len(warp_col)] if v else weft_col[r % len(weft_col)] for c, v in enumerate(row)] for r, row in enumerate(dd)]
TWILL = {0: {0, 1}, 1: {1, 2}, 2: {2, 3}, 3: {3, 0}}
DRAFTS = {
    "plain weave": ([0, 1], {0: {0}, 1: {1}}, [0, 1], [0], [1]),
    "2/2 twill": ([0, 1, 2, 3], TWILL, [0, 1, 2, 3], [0], [1]),
    "houndstooth": ([0, 1, 2, 3], TWILL, [0, 1, 2, 3], [0, 0, 0, 0, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1, 1, 1]),
    "chevron": ([0, 1, 2, 3, 0, 1, 2, 3, 2, 1, 0, 3, 2, 1], TWILL, [0, 1, 2, 3], [0], [1]),
}
def period(grid, axis):
    n = len(grid) if axis == 0 else len(grid[0])
    for p in range(1, n // 2 + 1):
        if axis == 0 and all(grid[r] == grid[r + p] for r in range(n - p)): return p
        if axis == 1 and all(row[c] == row[c + p] for row in grid for c in range(n - p)): return p
    return None
if __name__ == "__main__":
    out = {}
    for name, (th, tu, tr, wc, fc) in DRAFTS.items():
        dd = drawdown(th, tu, tr, 32, 32); col = colours(dd, wc, fc); out[name] = col
        print(f"{name:12s}: colour period rows {period(col, 0)}, cols {period(col, 1)}")
    plain = drawdown(*DRAFTS["plain weave"][:3], 8, 8)
    print("plain weave is a checkerboard:", all(plain[r][c] == (r + c + 1) % 2 for r in range(8) for c in range(8)))
    tw = drawdown(*DRAFTS["2/2 twill"][:3], 8, 8)
    print("2/2 twill: every row has half the warps up:", all(sum(row) == 4 for row in tw))
    hb = drawdown(*DRAFTS["chevron"][:3], 4, 14)
    print("chevron threading reverses (diagonal changes direction):", hb[0][:4] != hb[0][7:11])
    hp = (period(out["houndstooth"], 0), period(out["houndstooth"], 1))
    print("PREDICTION", "HELD" if hp == (8, 8) else "FAILED", f"(houndstooth period {hp}, predicted (8, 8))")
    (Path(__file__).resolve().parent / "weave.json").write_text(json.dumps(out), encoding="utf-8")
