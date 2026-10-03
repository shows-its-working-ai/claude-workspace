"""Cycle 79: the portrait's 'mistakes caught' dots are HAND-ENTERED in data.json; the prediction rings are derived
from the journal. Audit the hand count against the journal.
Prediction (written first): at least 5 cycles disagree (journal records a caught mistake but the count is 0, or
the count is > 0 but the journal records none).
Evidence = bold journal labels I use for caught mistakes: **Caught**, **Mistake(s)**, **Bug...**, **Snag**,
**Trap caught**, "The gate blocked", "Mistakes caught". Flags are listed for a manual read, not auto-corrected."""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
journal = (HERE.parents[1] / "JOURNAL.md").read_text(encoding="utf-8")
data = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
sections = {}
for m in re.finditer(r"^## Cycle (\d+) - [\d-]+ - (.+)$", journal, re.M):
    start = m.end(); nxt = re.search(r"^## ", journal[start:], re.M)
    sections[int(m.group(1))] = journal[start:start + (nxt.start() if nxt else len(journal))]
EVID = re.compile(r"\*\*(Caught|Mistakes?|Bugs?\b|Bug the|Snag|Trap caught)|The gate blocked|Mistakes caught|Caught on the way", re.I)
flags = []
for n, kind, caught, summary in data["cycles"]:
    hits = len(EVID.findall(sections[n]))
    if (caught == 0) != (hits == 0): flags.append((n, caught, hits))
print(f"{len(data['cycles'])} cycles; disagreements: {len(flags)}")
for n, c, h in flags: print(f"  cycle {n}: hand count {c}, journal evidence labels {h}")

# The reliable direction only: if the journal records a caught mistake with one of the labels, the count must be > 0.
# (The other direction is not checked: my wording for caught mistakes varies, so "no label" proves nothing;
#  cycle 79's manual read found 14 of 16 such flags were vocabulary misses.)
under = [(n, c, h) for n, c, h in flags if c == 0]
# cycle 95: since cycle 86 every journal entry states "(count N)", so for those cycles the hand-entered count must
# EQUAL the journal's (last stated) count, in both directions. A mutation typing cycle 94's count as 0 survived the
# one-way rule, because cycle 94's entry had no label at all.
strict = []
for n, kind, caught, summary in data["cycles"]:
    if n < 86: continue
    found = re.findall(r"\(count (\d+)\)|count \+\d+ -> (\d+)", sections[n])
    stated = int(found[-1][0] or found[-1][1]) if found else 0
    if stated != caught: strict.append((n, caught, stated))
if strict: print("COUNT MISMATCH (cycle, data, journal):", strict)
print("CAUGHT AUDIT OK" if not under and not strict else f"UNDERCOUNTED: {under}")
