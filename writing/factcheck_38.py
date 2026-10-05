"""Fact-check for writing/38-three-small-poems.md: 27's peak and steps == collatz.json; 169 circles up to 100 ==
apollo.json, the starting curvatures, and my guess of ~120 in cycle 210's journal; Sim's 112,096 positions, no draws,
second player wins == sim.py's output; and the Sim page really does start with 'you start' (you go first)."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "38-three-small-poems.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
c = json.loads((ROOT / "art/23-collatz/collatz.json").read_text(encoding="utf-8"))
check("27: peak 9,232, 111 steps", c["peak_27"] == 9232 and c["steps_27"] == 111 and "nine thousand two hundred and thirty-two" in s and "a hundred and eleven steps" in s)
a = json.loads((ROOT / "art/24-apollonian/apollo.json").read_text(encoding="utf-8"))
check("169 circles up to 100, starting -1, 2, 2, 3", a["count_le_100"] == 169 and a["curvatures_le_100"][:4] == [-1, 2, 2, 3]
      and "a hundred and sixty-nine" in s and "Minus one, two, two, three" in s)
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8"); sec = j.split("## Cycle 210 - ")[1].split("\n## ")[0] if "## Cycle 210 - " in j else ""
check("my guess was about 120 (journal 210)", "about 120 circles of curvature <= 100" in " ".join(sec.split()) and "I guessed a hundred and twenty" in s)
out = subprocess.run([sys.executable, str(ROOT / "projects/26-sim/sim.py")], capture_output=True, text=True).stdout
check("Sim: 112,096 positions, no draws, second player wins", "positions solved: 112096" in out and "(no draws): True" in out and "GUESS second player wins: True" in out
      and "a hundred and twelve thousand and ninety-six positions" in s and "It can never be a draw" in s and "The second player can always win" in s)
page = (ROOT / "projects/26-sim/index.html").read_text(encoding="utf-8")
check("the Sim page starts with you going first", "newGame(false);\n</script>" in page.replace("\r\n", "\n") and "and then I let you go first" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
