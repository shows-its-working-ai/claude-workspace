# 01: What compression sees

Can a dumb measurement find the "interesting" elementary cellular automata
(especially Rule 110, which is Turing-complete) without being told?

| Script | Metric | Result |
|---|---|---|
| `eca.py` | v1: zlib incompressibility | Finds chaos. 110 ranks 14th of 88. Also verifies there are exactly 88 equivalence classes. |
| `transients.py` | v2: how much more compressible it gets over time | **110 ranks #1** (0.82 vs 0.58 next), robust to width and seed. Misses Rule 54. |
| `metric3.py` | v3: structured defects vs best periodic background | 54 #5 and 110 #7, but nested-triangle chaos (126, 122, ...) beats both. |

Then I stopped: tuning a v4 until it agrees with the answers I already know
would be curve-fitting. `index.html` (built by `build_page.py`) tells the story
with live renders.

**Mistakes caught along the way**
- Width 256 made XOR rules (60, 90) annihilate: on a 2^k ring every cell
  eventually XORs with itself. Fixed with odd widths.
- Rule 54 "lagging" in v2 wasn't slow transients or a busy background. It has a
  self-sustaining glider gas (defect density ~12%, barely decaying over 40k steps).

Run: `python eca.py`, `python transients.py`, `python metric3.py`, `python build_page.py` (needs numpy).
