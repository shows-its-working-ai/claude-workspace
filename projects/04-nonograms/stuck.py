"""Show where logic gets stuck on a rejected picture: '#'/'.' = deduced, '?' = undetermined."""
import sys
from puzzles import PICTURES, grid, clues, line_solve
for name in sys.argv[1:]:
    sol = grid(PICTURES[name]); rc = [clues(r) for r in sol]; cc = [clues([r[j] for r in sol]) for j in range(len(sol[0]))]
    g, _ = line_solve(rc, cc)
    print(name)
    for r, s in zip(g, sol):
        print("  " + "".join("?" if v is None else "#" if v else "." for v in r) + "    " + "".join("#" if v else "." for v in s))
