"""Fact-check for writing/20-what-a-test-cant-hear.md: each footnoted quote appears verbatim in the journal section of
the cycle it's attributed to; "six things that make sound" == the number of published pages that create audio;
the pages the essay says state the limit really do (Glider Music mentions hearing; Ring Your Bell says "not by ear")."""
import re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "writing" / "20-what-a-test-cant-hear.md").read_text(encoding="utf-8")
body = s.split("### Fact-check")[0]
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
sec = {}
for m in re.finditer(r"^## Cycle (\d+) - [\d-]+ - .+$", j, re.M):
    st = m.end(); nx = re.search(r"^## ", j[st:], re.M); sec[int(m.group(1))] = j[st:st + (nx.start() if nx else len(j))]
lines = re.findall(r"^\d+\. Cycle (\d+): (.+)$", s.split("### Fact-check")[1], re.M)
check("5 footnotes", len(lines) == 5)
for n, rest in lines:
    for q in re.findall(r'"((?:[^"\\]|\\.)+)"', rest):
        q2 = q.replace("\\n", "\n")
        check(f"cycle {n} has: {q[:50]!r}", " ".join(q2.split()) in " ".join(sec.get(int(n), "").split()))   # words, not line breaks
        check(f"  ...and the essay body quotes it", " ".join(q2.split()) in " ".join(body.split()))
# cycle 160: "six" was checked against `git ls-files`, which can't see a page that isn't committed yet, so the gate
# passed just before the commit that made it seven. The claim is now "when I wrote this": count the pages in the commit
# that added the essay, and count today's pages including untracked ones.
def git(*a): return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
added = git("log", "--diff-filter=A", "--format=%H", "--", "writing/20-what-a-test-cant-hear.md").split()[-1]
then = sorted(f for f in git("ls-tree", "-r", "--name-only", added).split() if f.endswith(".html") and "template" not in f
              and "AudioContext" in git("show", f"{added}:{f}"))
now = sorted(f for f in git("ls-files", "--cached", "--others", "--exclude-standard", "*.html").split()
             if "template" not in f and "AudioContext" in (ROOT / f).read_text(encoding="utf-8", errors="ignore"))
check(f"'when I wrote this ... six' == {len(then)} pages with audio in the essay's commit", "When I wrote this I had made six things that make sound" in body and len(then) == 6, str(then))
check(f"'there are more now': {len(now)} today (untracked included)", "there are more now" in body and len(now) > 6, str(now))
gm = (ROOT / "art/04-glider-music/index.html").read_text(encoding="utf-8"); rb = (ROOT / "projects/13-ring-your-bell/index.html").read_text(encoding="utf-8")
check("Glider Music's page mentions not hearing it", "hear" in gm and "page for Glider Music says it" in body)
check("Ring Your Bell's page says 'not by ear'", "not by ear" in rb)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
