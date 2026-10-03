"""Fact-check for writing/07-the-scorecard.md: every quoted phrase in its fact-check list must appear
verbatim in JOURNAL.md, and the table's tally must match the numbers stated in the text."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "writing" / "07-the-scorecard.md").read_text(encoding="utf-8")
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
fc = s.split("### Fact-check")[1]
quotes = [q.replace('\\"', '"') for q in re.findall(r'"((?:[^"\\]|\\")+)"', fc)]
bad = [q for q in quotes if q not in j]
print(len(quotes), "quoted phrases; missing:", bad or "none")
rows = re.findall(r"^\| (\d+) \|.*\| (.+?) \[\d+\] \|$", s, re.M)
held = sum(o.startswith("Held") for _, o in rows)
failed = sum(o.startswith("Failed") for _, o in rows)
other = len(rows) - held - failed
print(f"table rows {len(rows)}: held {held}, failed {failed}, other {other}")
ok = not bad and (len(rows), held, failed, other) == (14, 5, 6, 3)
ok &= "Fourteen predictions in 36 cycles. Five held, six failed, three partly held (one of them just \"close\")." in s
ok &= "six held, eight failed, five partly held" in s       # + essay 04: 1 hit, 2 half, 2 miss
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
