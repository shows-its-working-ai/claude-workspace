# 02: Light the Path

Toggle cells in the shaded strip of the top row, press **Run**, and the
automaton grows downward. Win: every green ring lit, every red X dark,
toggles <= par. Open `index.html` in a browser; no install needed.

**Every level is checked:** `levels.py` brute-forces every toggle set up to
size 4 and confirms the level is solvable, that par is the true minimum, that
the solution is unique, and that the empty board loses. `quality.py` confirms
every mark is *necessary* (it rules out some attempt the other marks allow).
`playtest.py` plays every level by real mouse clicks in a headless browser.

**History**
- v1: 13 of 40 marks did nothing.
- v2: the marks are *constructed* (greedy elimination + pruning), giving 0 of 21 useless marks and unique solutions.
- The playtest caught a real bug: a stale win flag leaking between levels.

Rebuild: `python levels.py && python build.py`.
