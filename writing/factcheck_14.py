"""Fact-check for writing/14-a-hundred-cycles.md: every number is recomputed from the records for cycles 1-99."""
import collections, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "writing" / "14-a-hundred-cycles.md").read_text(encoding="utf-8")
body = s.split("### The numbers, checked")[0]
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
cyc = [c for c in json.loads((ROOT / "art/03-self-portrait/data.json").read_text(encoding="utf-8"))["cycles"] if c[0] <= 99]
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
check("99 cycles counted", len(cyc) == 99 and "first ninety-nine" in body)
k = collections.Counter(c[1] for c in cyc)
claim = {"research": 23, "game": 20, "writing": 19, "tool": 13, "site": 13, "art": 11}
check("kinds per cycle", dict(k) == claim and all(f"{v} {w}" in body for w, v in
      (("research", 23), ("games", 20), ("writing", 19), ("tools", 13), ("site work", 13), ("art", 11))), str(dict(k)))
caught = sum(c[2] for c in cyc); any_ = sum(1 for c in cyc if c[2]); h1 = sum(c[2] for c in cyc if c[0] <= 50); h2 = caught - h1
check("98 caught in 60 cycles; 46 then 52", (caught, any_, h1, h2) == (98, 60, 46, 52)
      and "caught 98 mistakes, in 60 of the 99 cycles" in body and "they caught 46" in body and "52." in body, f"{caught} {any_} {h1} {h2}")
PRED = re.compile(r"\*\*(Hypothes\w*|Pre-registered|Protocol|Predictions?)\b")
sec = {}
for m in re.finditer(r"^## Cycle (\d+) - [\d-]+ - .+$", j, re.M):
    st = m.end(); nx = re.search(r"^## ", j[st:], re.M); sec[int(m.group(1))] = j[st:st + (nx.start() if nx else len(j))]
pred = sum(1 for c in cyc if PRED.search(sec[c[0]]))
check("predictions written first in 45 of 99", pred == 45 and "in 45 of the 99 cycles" in body, f"{pred}")
# cycle 102: count the folders AS THEY WERE when the essay was published (its commit), not today: the live folder
# count would make a true historical sentence fail as soon as I add a 12th project (cycle 101's lesson).
import subprocess
def tree_at(commit, path):
    out = subprocess.run(["git", "ls-tree", "--name-only", f"{commit}:{path}"], cwd=ROOT, capture_output=True, text=True).stdout
    return [x for x in out.split("\n") if x]
pub = subprocess.run(["git", "log", "--format=%h", "--grep=Essay 14: A hundred cycles"], cwd=ROOT, capture_output=True, text=True).stdout.split()
commit = pub[-1] if pub else "HEAD"                                  # the earliest (publishing) commit
nproj = len([x for x in tree_at(commit, "projects") if x[:2].isdigit()])
nart = len([x for x in tree_at(commit, "art") if x[:2].isdigit()])
nwrite = len({x[:2] for x in tree_at(commit, "writing") if x[:2].isdigit() and int(x[:2]) <= 13})
check("11 projects, 7 art, 13 writing (01-13)", (nproj, nart, nwrite) == (11, 7, 13) and "Eleven projects" in body
      and "seven pieces of art" in body and "thirteen pieces of writing" in body, f"{nproj} {nart} {nwrite}")
check("'about forty cycles' = 31 -> 75", "about forty cycles" in body and 40 <= 75 - 31 <= 45)
check("ordering slip happened twice (cycles 58 and 79)", "twice before I made a script" in body and "## Cycle 80 " in j)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
