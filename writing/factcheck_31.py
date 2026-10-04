"""Fact-check for writing/31-why-hex-cant-draw.md: runs projects/20-hex/walk.py and checks the essay's numbers and
claims against its output: 65,536 fillings of the 4x4 board, every walk ends bottom-left or top-right and agrees with
the chain search, 32,768 each way on 4x4 (computed here per board size), and the "every one disagreed" remark about
the first version (recorded in the journal's cycle 194 section)."""
import re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "31-why-hex-cant-draw.md").read_text(encoding="utf-8").split())
out = subprocess.run([sys.executable, str(ROOT / "projects/20-hex/walk.py")], capture_output=True, text=True).stdout
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
check("walk.py: 65,536 4x4 fillings, 0 disagreements", "n=4: 65536 fillings walked; disagreements with brute force: 0" in out
      and "all 65,536 of them" in s and "named the same winner" in s)
check("walks end only bottom-left / top-right", re.search(r"where walks ended: \{'(top-right|bottom-left)': \d+, '(top-right|bottom-left)': \d+\}", out)
      and "ended at the bottom-left or the top-right corner" in s)
ns = {}; exec((ROOT / "projects/20-hex/hex.py").read_text(encoding="utf-8").split("out = {}")[0], ns)   # nbrs, wins
N = ns["nbrs"](4); red = sum(ns["wins"](4, [1 if m >> i & 1 else 2 for i in range(16)], 1, N) for m in range(1 << 16))
check(f"4x4: {red} red wins, {65536 - red} blue", red == 32768 and "32,768 red wins and 32,768 blue" in s)
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8"); sec = j.split("## Cycle 194 - ")[1].split("\n## ")[0] if "## Cycle 194 - " in j else ""
check("first version: every one of 65,536 disagreed (journal 194)", "65536" in sec and "every one" in sec.lower() and "Every one of the 65,536 boards disagreed" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
