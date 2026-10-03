"""Fact-check for writing/12-break-it-on-purpose.md: each quoted phrase must appear verbatim in JOURNAL.md, inside the
journal section for the cycle the essay attributes it to; and "about fifty" checks must match run_all.py."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "writing" / "12-break-it-on-purpose.md").read_text(encoding="utf-8")
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
sections = {}
for m in re.finditer(r"^## Cycle (\d+) - [\d-]+ - .+$", j, re.M):
    start = m.end(); nxt = re.search(r"^## ", j[start:], re.M)
    sections[int(m.group(1))] = j[start:start + (nxt.start() if nxt else len(j))]
fc = s.split("### Fact-check")[1]
lines = re.findall(r"^\d+\. Cycle (\d+): (.+)$", fc, re.M)
check(f"{len(lines)} fact-check lines, one per footnote", len(lines) == 4)
for line in lines:
    n, rest = int(line[0]), line[1]
    quotes = re.findall(r'"((?:[^"\\]|\\.)+)"', rest)   # cycle 93: \\. so a quote containing \n isn't silently skipped
    check(f"footnote for cycle {n} has at least one quote", quotes)
    for q in quotes:
        q = q.replace("\\n", "\n")
        check(f"cycle {n} contains: {q[:60]!r}", q in sections.get(n, ""))
n_checks = len(re.findall(r'^    \("', (ROOT / "run_all.py").read_text(encoding="utf-8"), re.M))
# cycle 101: "about fifty" was true WHEN WRITTEN (cycle 93: 53 checks). Comparing it with today's run_all.py (61) made
# a historical statement fail as the suite grew. Check it against the count recorded at the time instead.
m93 = re.search(r'"about fifty" checks vs run_all\.py \((\d+)\)', sections.get(93, ""))
then = int(m93.group(1)) if m93 else None
check(f"'about fifty' checks at the time of writing (cycle 93 recorded {then}; today {n_checks})",
      "about fifty of them" in s and then is not None and 40 <= then <= 60)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
