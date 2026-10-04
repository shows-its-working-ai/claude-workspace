"""Fact-check for writing/29-four-results.md, against the data the pages are tested with:
I   Hex: 2^16 = 65,536 fillings of the 4x4 board, none a draw (hex.py's run); II  n^2+n+41: starts at 41, steps of
2, 4, 6, prime for 40 values, the 41st = 41 x 41; III the ant: mess for 9,976 steps (highway from step 9,977, ant.json),
period 104, and the forever argument is forever.py's (squares left by the last round, or never touched); IV the
crossed box: 4 corners, all of degree 3 (One Stroke's figure), so no one-stroke drawing, and 2 odd corners would be
allowed. Each fact must still be stated in the poem."""
import json, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "29-four-results.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
ra = (ROOT / "run_all.py").read_text(encoding="utf-8")
check("I: 65,536 fillings, none a draw (hex.py's checked output)", 2 ** 16 == 65536 and "fillings with not exactly one winner: 0 of 65536" in ra
      and "Sixty-five thousand, five hundred and thirty-six ways" in s and "not one ends in a draw" in s)
isp = lambda m: m > 1 and all(m % f for f in range(2, int(m ** .5) + 1))
v = [n * n + n + 41 for n in range(41)]
check("II: 41, then +2, +4, +6", v[0] == 41 and [v[1] - v[0], v[2] - v[1], v[3] - v[2]] == [2, 4, 6] and "Start at forty-one and add two, then four, then six" in s)
check("II: forty primes in a row, then 41 x 41", all(map(isp, v[:40])) and v[40] == 41 * 41 and "forty times in a row" in s and "forty-one times forty-one" in s)
ant = json.loads((ROOT / "art/18-ant/ant.json").read_text(encoding="utf-8"))
check("III: mess for 9,976 steps, then period 104", ant["start"] - 1 == 9976 and ant["period"] == 104
      and "nine thousand, nine hundred and seventy-six steps" in s and "a hundred and four steps" in s)
fv = (ROOT / "art/18-ant/forever.py").read_text(encoding="utf-8")
check("III: the forever argument is forever.py's, and its certificate is in the suite",
      "whatever round k-i left there" in fv and "no highway round ever touched it" in fv and "certificate: round starting at step 9978" in ra
      and "I could show you it goes on forever" in s and "what it left itself, or nothing" in s)
page = (ROOT / "projects/21-stroke/index.html").read_text(encoding="utf-8")
m = re.search(r"name: 'Crossed box', pts: \[(.*?)\],\s*edges: \[(.*?)\]\}", page, re.S)
edges = [tuple(map(int, e)) for e in re.findall(r"\[(\d+), (\d+)\]", m.group(2))]
deg = [sum(c in e for e in edges) for c in range(4)]
check(f"IV: crossed box has 4 corners of degree 3 ({deg})", deg == [3, 3, 3, 3] and "Four corners, every one of them the end of three lines" in s)
check("IV: two odd ends allowed, four not", "Two can be where you start and stop. Four can't." in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
