# 02: Light the Path

Toggle cells in the shaded strip of the top row, press **Run**, and the
automaton grows downward. Win: every green ring lit, every red X dark,
toggles <= par. Open `index.html` in a browser; no install needed.

**Every level is checked:** `levels.py` brute-forces every toggle set up to
size 4 and confirms the level is solvable, that par is the true minimum, that
the solution is unique, and that the empty board loses. `quality.py` confirms
every mark is *necessary* (it rules out some attempt the other marks allow).
`playtest.py` plays every level by real mouse clicks in a headless browser.

**Levels:** 15. Chapter 1 (levels 1-8, frozen in `levels_ch1.json`) uses
rules 90, 150, 30, 110 and 54 on a 31x18 board. Chapter 2 (levels 9-12) is Rule 110
on a bigger 41x28 board with par up to 4. (From a blank background Rule 110 grows its
textured triangles. These are not true gliders, which need a periodic background.)
Chapter 3 (levels 13-15) starts on Rule 110's real periodic background, the
14-cell "ether", and every hidden solution launches a persistent glider. The gliders were
found by brute force (`glider_search.py`) and match the published A, C and E types.

**History**
- v1: 13 of 40 marks did nothing.
- v2: the marks are *constructed* (greedy elimination + pruning), giving 0 of 21 useless marks and unique solutions.
- Chapter 2: 0 of 37 useless marks across all 12 levels; every level has a unique solution; all 12 pass the click playtest.
- The playtest caught a real bug: a stale win flag leaking between levels.

Rebuild: `python levels.py && python build.py`.
