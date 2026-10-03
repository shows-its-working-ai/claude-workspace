"""Slide level quality (cycle 68). For each level: number of distinct SHORTEST solutions (counted by BFS layers),
and number of TRAPS: resting spots reachable from the start from which the goal can never be reached.
Prediction (written first): most of the 12 current levels have more than one shortest solution, and fewer than
half contain a trap."""
import json
from collections import deque
from pathlib import Path
from make_levels import slide
D = Path(__file__).resolve().parent

def analyse(L):
    grid, start, goal = L["grid"], tuple(L["start"]), tuple(L["goal"])
    nbr = {}
    dist, ways = {start: 0}, {start: 1}; q = deque([start])
    while q:                                                     # BFS over ALL reachable resting spots
        p = q.popleft(); nbr[p] = set()
        for d in "UDLR":
            n = slide(grid, *p, d)
            if n == p: continue
            nbr[p].add(n)
            if n not in dist: dist[n] = dist[p] + 1; ways[n] = 0; q.append(n)
            if dist[n] == dist[p] + 1: ways[n] += ways[p]
    can = {goal}; changed = True                                 # spots from which the goal is reachable
    while changed:
        changed = False
        for p, ns in nbr.items():
            if p not in can and ns & can: can.add(p); changed = True
    traps = [p for p in nbr if p not in can]
    return {"par": dist[goal], "shortest_solutions": ways[goal], "spots": len(nbr), "traps": len(traps)}
if __name__ == "__main__":
    levels = json.loads((D / "levels.json").read_text(encoding="utf-8"))
    rows = [analyse(L) for L in levels]
    for L, r in zip(levels, rows): print(f"{L['name']:9s} {r}")
    multi = sum(r["shortest_solutions"] > 1 for r in rows); trapped = sum(r["traps"] > 0 for r in rows)
    print(f"levels with >1 shortest solution: {multi}/12; with at least one trap: {trapped}/12")
    # cycle 68 standard: every level has exactly ONE shortest solution, and at least half have a trap
    print("QUALITY OK" if multi == 0 and trapped >= 6 else "QUALITY FAILED")
