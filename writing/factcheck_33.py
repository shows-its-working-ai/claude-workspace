"""Fact-check for writing/33-twenty-minutes.md, against the journal: the three issue times (cycle 205's record) span
about twenty minutes; the reader's quoted words appear in the journal's cycle 200/201 sections; "about a hundred and
thirty" checks and "seventy-odd" planted bugs AS OF the commit that added the essay (cycle 183's rule); the four bugs
found by auditing are the ones cycles 203 and 204 record; "Fix #2" auto-closed issue #2 (cycle 200)."""
import re, subprocess
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "33-twenty-minutes.md").read_text(encoding="utf-8").split())
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
sec = {}
for m in re.finditer(r"^## Cycle (\d+) - [\d-]+ - .+$", j, re.M):
    st = m.end(); nx = re.search(r"^## ", j[st:], re.M); sec[int(m.group(1))] = " ".join(j[st:st + (nx.start() if nx else len(j))].split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
times = re.findall(r"(\d\d:\d\d:\d\d)Z", sec.get(205, ""))[:3]
span = (datetime.strptime(times[2], "%H:%M:%S") - datetime.strptime(times[0], "%H:%M:%S")).seconds / 60 if len(times) == 3 else 0
check(f"three issues within ~20 minutes ({span:.1f} min)", len(times) == 3 and 15 <= span <= 25 and "three issues in twenty minutes" in s)
for q, c in (("i can play multiple methods at once overlapping each other", 200), ("i cant see the colors anymore", 201)):
    check(f"reader's words in cycle {c}: {q!r}", q in sec.get(c, "") and q in s)
git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
added = (git("log", "--diff-filter=A", "--format=%H", "--", "writing/33-twenty-minutes.md").split() or ["HEAD"])[-1]
src = lambda f: git("show", f"{added}:{f}") if added != "HEAD" else (ROOT / f).read_text(encoding="utf-8")
n_checks = len(re.findall(r'^    \("', src("run_all.py"), re.M)); n_mut = len(re.findall(r'^    \("', src("tools/mutate.py"), re.M))
check(f"'about a hundred and thirty' checks then ({n_checks} listed; ~130 run quick)", 125 <= n_checks <= 160 and "about a hundred and thirty run" in s)
check(f"'about eighty' planted bugs then ({n_mut})", 75 <= n_mut <= 89 and "about eighty deliberate bugs" in s)   # v1 said seventy-odd with a 70..89 range that waved 82 through
check("four more bugs: Ring Your Bell + Against (203), two games (204)", all(w in sec.get(203, "") for w in ("Ring Your Bell", "Against"))
      and "Nobody Wins Noughts" in sec.get(204, "") and "Four Boxes" in sec.get(204, "") and "There were four more." in s)
check("'Fix #2' auto-closed issue #2 (cycle 200)", "Fix #2" in sec.get(200, "") and "CLOSE issue #2 automatically" in sec.get(200, "") and "Fix #2" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
