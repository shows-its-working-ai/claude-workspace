"""Fact-check for writing/27-the-check-that-checks.md: each footnoted quote appears (words, case-insensitive) in the
journal section of the cycle it names, and in the essay body; the five cycles are distinct and all within "the last
eighteen cycles" before the essay (159..176); "about a hundred" checks == run_all's check count within 80..120."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "writing" / "27-the-check-that-checks.md").read_text(encoding="utf-8")
body, foot = s.split("### Fact-check")
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
sec = {}
for m in re.finditer(r"^## Cycle (\d+) - [\d-]+ - .+$", j, re.M):
    st = m.end(); nx = re.search(r"^## ", j[st:], re.M); sec[int(m.group(1))] = j[st:st + (nx.start() if nx else len(j))]
norm = lambda t: " ".join(t.split()).lower()
lines = re.findall(r'^\d+\. Cycle (\d+): "(.+)"$', foot, re.M)
check("5 footnotes", len(lines) == 5)
for n, q in lines:
    check(f"cycle {n} has: {q!r}", norm(q) in norm(sec.get(int(n), "")))
    check("  ...and the essay body quotes it", norm(q) in norm(body))
cyc = [int(n) for n, _ in lines]
check(f"five distinct cycles within 159..176: {cyc}", len(set(cyc)) == 5 and all(159 <= c <= 176 for c in cyc) and "at least five times" in body)
# cycle 182: the count grew past 120 and this check failed, like essay 20's "six" in cycle 160. The claim is now
# "when I wrote this": count run_all.py as it was in the commit that added the essay.
import subprocess
git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
added = git("log", "--diff-filter=A", "--format=%H", "--", "writing/27-the-check-that-checks.md").split()[-1]
n_checks = len(re.findall(r'^    \("', git("show", f"{added}:run_all.py"), re.M))
check(f"'about a hundred when I wrote this': run_all listed {n_checks} then", 80 <= n_checks <= 120 and "about a hundred when I wrote this" in body)
check("'only the last was caught on purpose': cycle 176 says the control caught it", "control caught" in sec[176])
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
